"""
FastAPI Backend Server para NotebookLM
Actúa como puente entre Streamlit y la API de NotebookLM
"""
import os
import asyncio
import subprocess
import time
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


# ============================================================================
# Re-autenticacion Automatica
# ============================================================================

# Control de tiempo para evitar re-auth excesivos
last_reauth_time = 0
REAUTH_COOLDOWN = 30  # Segundos minimos entre re-autenticaciones

def auto_reauth() -> bool:
    """
    Ejecuta notebooklm-mcp-auth --file automaticamente para renovar credenciales.
    Usa el archivo cookies.txt del directorio del proyecto si existe.
    Retorna True si tuvo exito, False en caso contrario.
    """
    global last_reauth_time

    current_time = time.time()

    # Evitar re-auth muy frecuentes
    if current_time - last_reauth_time < REAUTH_COOLDOWN:
        print(f"[REAUTH] Cooldown activo. Esperando {REAUTH_COOLDOWN}s entre re-autenticaciones.")
        return False

    # Buscar archivo cookies.txt
    project_dir = Path(__file__).parent
    cookies_file = project_dir / "cookies.txt"

    if not cookies_file.exists():
        print("[REAUTH] No existe cookies.txt - re-autenticacion automatica no disponible")
        print("[REAUTH] Para habilitar re-auth automatica:")
        print("  1. Abre Chrome -> notebooklm.google.com")
        print("  2. F12 -> Network -> filtrar 'batchexecute'")
        print("  3. Copia el header 'cookie' y guardalo en cookies.txt")
        return False

    print(f"[REAUTH] Encontrado cookies.txt, iniciando re-autenticacion...")

    try:
        # Ejecutar notebooklm-mcp-auth --file pasando el archivo por stdin
        result = subprocess.run(
            ["notebooklm-mcp-auth", "--file"],
            input=str(cookies_file) + "\n",
            capture_output=True,
            text=True,
            timeout=60
        )

        last_reauth_time = time.time()

        if result.returncode == 0:
            print("[REAUTH] Re-autenticacion exitosa!")
            print(f"[REAUTH] Output: {result.stdout[:300] if result.stdout else 'OK'}")
            return True
        else:
            print(f"[REAUTH] Fallo con codigo {result.returncode}")
            print(f"[REAUTH] STDOUT: {result.stdout[:500] if result.stdout else 'Vacio'}")
            print(f"[REAUTH] STDERR: {result.stderr[:500] if result.stderr else 'Vacio'}")
            return False

    except subprocess.TimeoutExpired:
        print("[REAUTH] Timeout - la re-autenticacion tardo demasiado")
        last_reauth_time = time.time()
        return False
    except FileNotFoundError:
        print("[REAUTH] Error: notebooklm-mcp-auth no encontrado en PATH")
        return False
    except Exception as e:
        print(f"[REAUTH] Error inesperado: {e}")
        last_reauth_time = time.time()
        return False


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
    Realiza una consulta con re-autenticacion automatica si es necesario.
    Flujo de reintentos:
      1. Intento normal
      2. Si falla auth -> recargar tokens del disco
      3. Si sigue fallando -> ejecutar auto_reauth() y reintentar
    """
    global client

    # FORZAR re-carga de tokens en cada consulta para asegurar que
    # si el usuario hizo re-login, lo pillemos al vuelo.
    init_client()

    print(f"[QUERY] Consulta recibida: {request.question[:50]}...")

    async def execute_query():
        """Ejecuta la consulta contra NotebookLM"""
        full_query = request.question

        with open("debug_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n--- NUEVA CONSULTA ---\nPregunta: {full_query[:100]}...\n")

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

        if isinstance(result, dict):
            answer = result.get("answer") or result.get("text") or result.get("content") or ""
            conv_id = result.get("conversation_id")
        else:
            answer = str(result)
            conv_id = None

        with open("debug_log.txt", "a", encoding="utf-8") as f:
            f.write(f"RESPUESTA EXTRAIDA: {answer[:100] if answer else 'VACIA'}...\n")
            f.write("----------------------\n")

        return QueryResponse(
            success=True,
            answer=answer,
            conversation_id=conv_id
        )

    try:
        # Intento 1: Consulta normal
        print("[RETRY] Intento 1/3: Consulta normal...")
        try:
            return await execute_query()
        except AuthenticationError as e:
            print(f"[WARN] Error de autenticacion en intento 1: {e}")

        # Intento 2: Recargar tokens del disco
        print("[RETRY] Intento 2/3: Recargando tokens del disco...")
        init_client(force_refresh=True)
        try:
            return await execute_query()
        except AuthenticationError as e:
            print(f"[WARN] Error de autenticacion en intento 2: {e}")

        # Intento 3: Re-autenticacion automatica
        print("[RETRY] Intento 3/3: Ejecutando re-autenticacion automatica...")
        reauth_success = await asyncio.to_thread(auto_reauth)

        if reauth_success:
            # Recargar cliente con nuevos tokens
            init_client(force_refresh=True)
            try:
                return await execute_query()
            except AuthenticationError as e:
                print(f"[ERROR] Error incluso despues de re-auth: {e}")
                raise e
        else:
            print("[ERROR] Re-autenticacion automatica fallida")
            raise AuthenticationError("Re-autenticacion automatica fallida. Verifica que Chrome este logueado en Google.")

    except AuthenticationError as e:
        print(f"[ERROR] Error final de autenticacion: {e}")
        raise HTTPException(
            status_code=401,
            detail=f"Error de autenticacion: {str(e)}. Si el problema persiste, ejecuta 'notebooklm-mcp-auth --file' manualmente."
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
