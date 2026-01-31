"""
Chat Streamlit para NotebookLM
Conecta con el servidor FastAPI para consultar NotebookLM
"""
import streamlit as st
import requests
import json

# ============================================================================
# Configuración
# ============================================================================

# Configuración
try:
    if "API_BASE_URL" in st.secrets:
        API_BASE_URL = st.secrets["API_BASE_URL"]
    else:
        API_BASE_URL = "http://localhost:8000"
except FileNotFoundError:
    API_BASE_URL = "http://localhost:8000"
except Exception:
    # Captura StreamlitSecretNotFoundError y otros errores de configuración
    API_BASE_URL = "http://localhost:8000"

NOTEBOOK_ID = "8442d244-d797-48fe-b495-21d053e6ac4e"

# ============================================================================
# Configuración de la página
# ============================================================================

st.set_page_config(
    page_title="Chat NotebookLM - YouTube IA Strategy",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    h1 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .status-connected {
        color: #00ff00;
        font-weight: bold;
    }
    .status-disconnected {
        color: #ff0000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Funciones de API
# ============================================================================

def check_api_health() -> dict:
    """Verifica el estado del servidor FastAPI"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "authenticated": False}
    except requests.exceptions.ConnectionError:
        return {"status": "disconnected", "authenticated": False, "error": "No se puede conectar al servidor API"}
    except Exception as e:
        return {"status": "error", "authenticated": False, "error": str(e)}


def query_notebooklm(question: str, notebook_id: str, conversation_id: str = None) -> dict:
    """Realiza una consulta al cuaderno vía FastAPI"""
    try:
        payload = {
            "question": question,
            "notebook_id": notebook_id,
            "conversation_id": conversation_id,
            "timeout": 120
        }
        
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=payload,
            timeout=130  # Un poco más que el timeout de la query
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return {
                "success": False,
                "error": "Error de autenticación. Ejecuta 'notebooklm-mcp-auth' en la terminal."
            }
        elif response.status_code == 503:
            return {
                "success": False,
                "error": "Servidor API no inicializado correctamente."
            }
        else:
            return {
                "success": False,
                "error": f"Error HTTP {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "❌ No se puede conectar al servidor API. Asegúrate de que esté corriendo en localhost:8000"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "⏱️ Timeout: La consulta tardó demasiado. Intenta con una pregunta más simple."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        }


def get_notebooks() -> list:
    """Obtiene la lista de cuadernos disponibles"""
    try:
        response = requests.get(f"{API_BASE_URL}/notebooks", timeout=30)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


# ============================================================================
# Interfaz de Usuario
# ============================================================================

# Título principal
st.title("🤖 Chat con NotebookLM")
st.markdown("### Estrategia YouTube IA y Formación School")

# Sidebar
with st.sidebar:
    st.header("📚 Panel de Control")
    
    # Verificar estado del servidor
    api_status = check_api_health()
    
    if api_status.get("status") == "ok":
        if api_status.get("authenticated"):
            st.success("✅ Conectado a NotebookLM")
        else:
            st.warning("⚠️ API activa pero no autenticada")
    else:
        st.error("❌ API desconectada")
        st.markdown("""
        **Para iniciar el servidor:**
        ```bash
        python api_server.py
        ```
        """)
    
    st.markdown("---")
    
    # Información del cuaderno
    st.info(f"""
    **Cuaderno activo:**  
    Estrategia YouTube IA y Formación School
    
    **Áreas de conocimiento:**
    - Estrategia de Contenido
    - Algoritmo y SEO YouTube
    - Conocimiento Técnico en IA
    - Automatización de Procesos
    - Community Building
    - Diseño Instruccional
    - Marketing y Conversión
    """)
    
    st.markdown("---")
    st.markdown("**💡 Ejemplos de preguntas:**")
    st.markdown("""
    - ¿Qué área tiene más futuro?
    - ¿Cómo implementar RAG?
    - Dame ideas de contenido para YouTube
    - ¿Qué herramientas de automatización recomiendas?
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Limpiar Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.rerun()
    
    with col2:
        if st.button("🔌 Reconectar", use_container_width=True):
            st.rerun()


# ============================================================================
# Chat
# ============================================================================

# Inicializar estado de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

# Mostrar mensajes del historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    # Verificar conexión primero
    api_status = check_api_health()
    
    if api_status.get("status") != "ok":
        st.error("❌ No hay conexión con el servidor API. Inicia el servidor con: `python api_server.py`")
    else:
        # Añadir mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Obtener respuesta del assistant
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🔍 Consultando NotebookLM...")
            
            # Realizar la consulta
            result = query_notebooklm(
                question=prompt,
                notebook_id=NOTEBOOK_ID,
                conversation_id=st.session_state.conversation_id
            )
            
            if result.get("success"):
                response = result.get("answer", "No se recibió respuesta")
                
                # Actualizar conversation_id para mantener contexto
                if result.get("conversation_id"):
                    st.session_state.conversation_id = result["conversation_id"]
                
                # Mostrar respuesta
                message_placeholder.markdown(response)
                
                # Añadir al historial
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                error_msg = f"❌ {result.get('error', 'Error desconocido')}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})


# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: white;'>
        <small>🚀 Potenciado por NotebookLM | FastAPI + Streamlit</small>
    </div>
    """,
    unsafe_allow_html=True
)
