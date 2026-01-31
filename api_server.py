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


def init_client():
    """Inicializa el cliente NotebookLM con tokens cacheados o variables de entorno"""
    global client
    
    # 1. Intentar cargar desde Variables de Entorno (Cloud/Render)
    cookie_header = os.environ.get("NOTEBOOKLM_COOKIES", "")
    if cookie_header:
        print("☁️ Usando autenticación por variables de entorno (Cloud)")
        try:
            # Función auxiliar para parsear cookies string a dict
            cookies = {}
            for item in cookie_header.split(";"):
                if "=" in item:
                    k, v = item.strip().split("=", 1)
                    cookies[k] = v
            
            client = NotebookLMClient(cookies=cookies)
            print("✅ Cliente NotebookLM inicializado desde Env Vars")
            return True
        except Exception as e:
            print(f"❌ Error parseando cookies de entorno: {e}")
    
    # 2. Intentar cargar desde archivo local (Desarrollo)
    print("📂 Buscando tokens locales...")
    tokens = load_cached_tokens()
    if not tokens:
        print("❌ No se encontraron tokens de autenticación (ni Env ni Local)")
        print("   Ejecuta: notebooklm-mcp-auth para autenticarte primero")
        return False
    
    try:
        client = NotebookLMClient(
            cookies=tokens.cookies,
            csrf_token=tokens.csrf_token,
            session_id=tokens.session_id
        )
        print("✅ Cliente NotebookLM inicializado desde archivo local")
        return True
    except Exception as e:
        print(f"❌ Error inicializando cliente: {e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Iniciando servidor FastAPI para NotebookLM...")
    init_client()
    yield
    # Shutdown
    print("👋 Cerrando servidor...")


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
    Realiza una consulta al cuaderno NotebookLM
    """
    if not client:
        raise HTTPException(
            status_code=503,
            detail="Cliente NotebookLM no inicializado. Ejecuta 'notebooklm-mcp-auth' primero."
        )
    
    try:
        # Implementar lógica de reintento automático (1 vez)
        for attempt in range(2):
            try:
                # Realizar la consulta de forma síncrona
                result = await asyncio.to_thread(
                    client.query,
                    notebook_id=request.notebook_id,
                    query_text=request.question,
                    conversation_id=request.conversation_id,
                    timeout=request.timeout
                )
                
                # Extraer la respuesta
                answer = result.get("answer", "") if isinstance(result, dict) else str(result)
                conv_id = result.get("conversation_id") if isinstance(result, dict) else None
                
                return QueryResponse(
                    success=True,
                    answer=answer,
                    conversation_id=conv_id
                )
                
            except AuthenticationError as e:
                if attempt == 0:
                    print(f"⚠️ Error de autenticación en intento 1: {e}")
                    print("🔄 Intentando refrescar tokens y reintentar...")
                    # Si refresca con éxito, el loop continúa
                    if init_client():
                        continue 
                
                # Si fallamos en el segundo intento o no pudimos refrescar, relanzar para que lo capture el outer except
                raise e

    except AuthenticationError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Error de autenticación: {str(e)}. Ejecuta 'notebooklm-mcp-auth' para renovar tokens."
        )
    except Exception as e:
        return QueryResponse(
            success=False,
            error=str(e)
        )


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
    print("🚀 NotebookLM Bridge API Server")
    print("=" * 60)
    print()
    print("📍 Servidor: http://localhost:8000")
    print("📖 Documentación: http://localhost:8000/docs")
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
