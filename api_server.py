"""
FastAPI Backend Server para NotebookLM
Actúa como puente entre Streamlit y la API de NotebookLM
"""
import os
import asyncio
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx  # Para manejar excepciones HTTP específicas
import json
from pathlib import Path

# Importar las bibliotecas de NotebookLM MCP
from notebooklm_mcp.auth import load_cached_tokens
from notebooklm_mcp.api_client import NotebookLMClient, AuthenticationError


# ============================================================================
# Modelos Pydantic
# ============================================================================

class QueryRequest(BaseModel):
    question: str
    notebook_id: str
    conversation_id: Optional[str] = None
    timeout: Optional[int] = 120


class QueryResponse(BaseModel):
    success: bool
    answer: Optional[str] = None
    conversation_id: Optional[str] = None
    error: Optional[str] = None


class NotebookInfo(BaseModel):
    id: str
    title: str
    source_count: int
    url: str


class HealthResponse(BaseModel):
    status: str
    message: str
    authenticated: bool


# ============================================================================
# Cliente Global
# ============================================================================

# Cliente NotebookLM (se inicializa al startup)
client: Optional[NotebookLMClient] = None


# Importar CLI de auth para refresco automático
try:
    from notebooklm_mcp.auth_cli import run_headless_auth
except ImportError:
    run_headless_auth = None

def init_client(force_refresh: bool = False):
    """
    Inicializa el cliente NotebookLM con tokens del archivo auth.json.
    """
    global client
    
    # 1. Cargar desde Variables de Entorno (Prioridad Nube)
    cookie_header = os.environ.get("NOTEBOOKLM_COOKIES", "")
    if cookie_header:
        try:
            cookies = {}
            for item in cookie_header.split(";"):
                if "=" in item:
                    k, v = item.strip().split("=", 1)
                    cookies[k] = v
            client = NotebookLMClient(cookies=cookies)
            print("[Cloud] Cliente inicializado con Env Vars")
            return True
        except Exception as e:
            print(f"[ERROR] Error cookies env: {e}")

    # 2. Carga desde Disco (Manual para evitar cache de la librería)
    auth_file = Path.home() / ".notebooklm-mcp" / "auth.json"
    print(f"[INFO] Cargando tokens frescos desde {auth_file}...")
    
    if not auth_file.exists():
        print("[ERROR] No se encontro auth.json. Usa 'notebooklm-mcp-auth'.")
        return False
    
    try:
        with open(auth_file, "r") as f:
            data = json.load(f)
        
        # Re-inicializar cliente con datos frescos
        client = NotebookLMClient(
            cookies=data.get("cookies", {}),
            csrf_token=data.get("csrf_token"),
            session_id=data.get("session_id")
        )
        print("[OK] Cliente NotebookLM sincronizado con disco (Manual)")
        return True
    except Exception as e:
        print(f"[ERROR] Error al instanciar cliente: {e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    # Startup
    print("[START] Iniciando servidor FastAPI para NotebookLM...")
    init_client()
    yield
    # Shutdown
    print("[STOP] Cerrando servidor...")


# ============================================================================
# Aplicación FastAPI
# ============================================================================

app = FastAPI(
    title="NotebookLM Bridge API",
    description="API puente para conectar aplicaciones frontend con NotebookLM",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS para permitir requests desde Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Endpoint raíz - información del servidor"""
    return HealthResponse(
        status="ok",
        message="NotebookLM Bridge API activa",
        authenticated=client is not None
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check del servidor"""
    return HealthResponse(
        status="ok",
        message="Servidor funcionando correctamente",
        authenticated=client is not None
    )


@app.post("/query", response_model=QueryResponse)
async def query_notebook(request: QueryRequest):
    """
    Realiza una consulta asegurando sincronización total con auth.json
    """
    global client
    
    # FORZAR re-carga de tokens en cada consulta para asegurar que 
    # si el usuario hizo re-login, lo pillemos al vuelo.
    init_client()
    
    print(f"[QUERY] Consulta recibida: {request.question[:50]}...")
    
    try:
        # Implementar lógica de reintento automático (1 vez)
        for attempt in range(2):
            try:
                print(f"[RETRY] Intento {attempt + 1}/2...")
                
                # Enviar la pregunta limpia para que NotebookLM use su propio contexto optimizado
                full_query = request.question
                
                with open("debug_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n--- NUEVA CONSULTA ---\nPregunta: {full_query}\n")

                # Realizar la consulta de forma síncrona
                result = await asyncio.to_thread(
                    client.query,
                    notebook_id=request.notebook_id,
                    query_text=full_query,
                    conversation_id=request.conversation_id,
                    timeout=request.timeout
                )
                
                with open("debug_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"RESULTADO BRUTO: {result}\n")
                    f.write(f"TIPO: {type(result)}\n")
                
                # Extraer la respuesta de forma más robusta
                if isinstance(result, dict):
                    answer = result.get("answer") or result.get("text") or result.get("content") or ""
                    conv_id = result.get("conversation_id")
                else:
                    answer = str(result)
                    conv_id = None
                
                with open("debug_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"RESPUESTA EXTRAIDA: {answer}\n")
                    f.write("----------------------\n")
                
                return QueryResponse(
                    success=True,
                    answer=answer,
                    conversation_id=conv_id
                )
                
            except AuthenticationError as e:
                print(f"[WARN] Error de autenticacion en intento {attempt + 1}: {e}")
                if attempt == 0:
                    print("[RETRY] Intentando refrescar tokens (Headless) y reintentar...")
                    if init_client(force_refresh=True):
                        continue 
                raise e
            except Exception as e:
                print(f"[DEBUG] Excepcion en intento {attempt + 1}: {type(e).__name__}: {e}")
                raise e

    except AuthenticationError as e:
        print(f"[ERROR] Error final de autenticacion: {e}")
        raise HTTPException(
            status_code=401,
            detail=f"Error de autenticación: {str(e)}. Ejecuta 'notebooklm-mcp-auth' para renovar tokens."
        )
    except httpx.HTTPStatusError as e:
        error_detail = f"Error HTTP {e.response.status_code}: {e.response.text[:200]}"
        print(f"[ERROR] HTTPStatusError: {error_detail}")
        return QueryResponse(
            success=False,
            error=f"Error del servidor NotebookLM ({e.response.status_code})."
        )
    except Exception as e:
        print(f"[ERROR] Error inesperado: {type(e).__name__}: {e}")
        return QueryResponse(
            success=False,
            error=f"Error inesperado: {type(e).__name__}: {str(e)}"
        )


@app.get("/debug-tokens")
async def debug_tokens():
    """Muestra qué cuenta está cargada actualmente"""
    tokens = load_cached_tokens()
    if not tokens:
        return {"status": "error", "message": "No se encontraron tokens en disco"}
    
    # Extraer un fragmento seguro de la cookie para identificación
    psid = tokens.cookies.get("__Secure-3PSID", "N/A")
    return {
        "status": "ok",
        "psid_prefix": psid[:15] + "...",
        "csrf_present": bool(tokens.csrf_token),
        "session_id": tokens.session_id,
        "active_notebook": "0523ea1e-7973-400a-a749-55a805205030"
    }


@app.get("/notebooks", response_model=list[NotebookInfo])
async def list_notebooks():
    """Lista todos los cuadernos disponibles"""
    if not client:
        raise HTTPException(
            status_code=503,
            detail="Cliente NotebookLM no inicializado"
        )
    
    try:
        notebooks = await asyncio.to_thread(client.list_notebooks)
        return [
            NotebookInfo(
                id=nb.id,
                title=nb.title,
                source_count=nb.source_count,
                url=nb.url
            )
            for nb in notebooks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notebook/{notebook_id}")
async def get_notebook(notebook_id: str):
    """Obtiene información detallada de un cuaderno"""
    if not client:
        raise HTTPException(
            status_code=503,
            detail="Cliente NotebookLM no inicializado"
        )
    
    try:
        notebook = await asyncio.to_thread(client.get_notebook, notebook_id)
        return {
            "id": notebook.id,
            "title": notebook.title,
            "source_count": notebook.source_count,
            "sources": notebook.sources,
            "url": notebook.url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/refresh-auth")
async def refresh_auth():
    """Intenta refrescar la autenticación"""
    success = init_client()
    if success:
        return {"status": "success", "message": "Autenticación refrescada"}
    else:
        raise HTTPException(
            status_code=401,
            detail="No se pudo refrescar la autenticación. Ejecuta 'notebooklm-mcp-auth'"
        )


# ============================================================================
# Punto de entrada
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("NotebookLM Bridge API Server")
    print("=" * 60)
    print()
    print("Servidor: http://localhost:8000")
    print("Documentacion: http://localhost:8000/docs")
    print()
    print("Endpoints disponibles:")
    print("  GET  /           - Health check")
    print("  GET  /health     - Health check")
    print("  POST /query      - Consultar cuaderno")
    print("  GET  /notebooks  - Listar cuadernos")
    print("  GET  /notebook/{id} - Obtener cuaderno")
    print()
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
