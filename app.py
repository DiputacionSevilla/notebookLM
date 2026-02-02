"""
Chat Streamlit Premium para NotebookLM
Adaptado para el Presupuesto 2026 - Diputación de Sevilla
"""
import streamlit as st
import requests
import json
import base64

# ============================================================================
# Configuración
# ============================================================================

try:
    if "API_BASE_URL" in st.secrets:
        API_BASE_URL = st.secrets["API_BASE_URL"]
    else:
        API_BASE_URL = "http://127.0.0.1:8000"
except Exception:
    API_BASE_URL = "http://127.0.0.1:8000"

# ID del cuaderno (Actualizado para el nuevo contexto si es necesario,
# por ahora mantenemos el ID pero el usuario indicó que el contenido cambió)
NOTEBOOK_ID = "0523ea1e-7973-400a-a749-55a805205030"

# Instrucciones del sistema para NotebookLM
SYSTEM_INSTRUCTIONS = """
INSTRUCCIONES OBLIGATORIAS:
- Responde SIEMPRE en castellano (espanol de Espana).
- Basate UNICAMENTE en la informacion contenida en las fuentes del notebook.
- NO inventes, supongas ni extrapoles informacion que no este en las fuentes.
- Si no dispones de la informacion solicitada, responde claramente: "No dispongo de esa informacion en las fuentes disponibles."
- Cita las fuentes cuando sea posible.

CONSULTA DEL USUARIO:
"""

# ============================================================================
# Configuración de la página
# ============================================================================

st.set_page_config(
    page_title="Presupuesto 2026 - Dipu Sevilla",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos Premium de Alto Contraste (Cero Fallos Visuales)
def local_css():
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@500;700&display=swap" rel="stylesheet">
    
    <style>
        /* Base and Typography */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #ffffff;
        }
        
        h1, h2, h3 {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            color: #ffffff !important;
        }

        /* Main Container Background - El original que gustaba */
        .stApp {
            background-color: #0e1117;
            background-image: 
                radial-gradient(at 0% 0%, rgba(34, 197, 94, 0.2) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(26, 115, 232, 0.2) 0px, transparent 50%);
        }

        /* Sidebar Styling (Sólido para evitar transparencias fallidas) */
        section[data-testid="stSidebar"] {
            background-color: #1a1e26 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {
            color: #ffffff !important;
        }

        /* Chat Messages (Sólidos y contrastados) */
        [data-testid="stChatMessage"] {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        }

        /* User Message (Highlight en Azul/Verde) */
        [data-testid="stChatMessage"]:nth-child(even) {
            background-color: #0f172a !important;
            border: 1px solid #1e40af !important;
        }

        /* Full white text forced for EVERYTHING in messages */
        [data-testid="stChatMessage"] * {
            color: #ffffff !important;
            font-size: 1.1rem !important;
            line-height: 1.6 !important;
        }

        /* Titles and Text (Grande y brillante) */
        .big-title {
            color: #ffffff;
            font-size: 4rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
            text-align: left;
            line-height: 1.1;
            text-shadow: 0 2px 10px rgba(34, 197, 94, 0.5);
        }
        
        .subtitle {
            color: #34d399; /* Verde esmeralda brillante */
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 2rem;
        }

        /* Custom widgets */
        .stButton>button {
            border-radius: 8px;
            font-weight: 800;
            background-color: #10b981 !important;
            color: white !important;
            border: none;
            padding: 0.8rem !important;
        }
        
        .stButton>button:hover {
            background-color: #059669 !important;
            box-shadow: 0 5px 15px rgba(16, 185, 129, 0.4);
        }

        /* Sidebar info box */
        .sidebar-info {
            background-color: #0f172a;
            padding: 1rem;
            border-radius: 10px;
            border-left: 5px solid #10b981;
            margin-bottom: 1rem;
            color: #ffffff !important;
        }

        /* Status colors */
        .status-online { color: #4ade80 !important; font-weight: bold; }
        .status-offline { color: #f87171 !important; font-weight: bold; }

        /* Hide Streamlit components */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

local_css()

# ============================================================================
# Funciones de API
# ============================================================================

@st.cache_data(ttl=60)
def check_api_health() -> dict:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "authenticated": False}
    except Exception:
        return {"status": "disconnected", "authenticated": False}

def query_notebooklm(question: str, notebook_id: str, conversation_id: str = None) -> dict:
    try:
        # Concatenar instrucciones del sistema con la pregunta del usuario
        full_question = SYSTEM_INSTRUCTIONS + question

        payload = {
            "question": full_question,
            "notebook_id": notebook_id,
            "conversation_id": conversation_id,
            "timeout": 120
        }
        response = requests.post(f"{API_BASE_URL}/query", json=payload, timeout=130)
        if response.status_code == 200:
            return response.json()
        return {"success": False, "error": f"Error {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# Interfaz de Usuario
# ============================================================================

# Header adaptable
st.markdown('<p class="big-title">Chat con el presupuesto de la Dipu</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análisis inteligente del Presupuesto 2026 - Diputación de Sevilla</p>', unsafe_allow_html=True)

# Sidebar Premium
with st.sidebar:
    try:
        st.image("logo-dipu.png", use_container_width=True)
    except:
        st.markdown("🏛️ **Diputación de Sevilla**")
    
    st.markdown("## ⚙️ Configuración")
    
    # Estado de la conexión
    health = check_api_health()
    if health.get("status") == "ok":
        st.markdown('<div style="color: #4ade80; font-size: 0.9rem; font-weight: 600;">● Sistema en Línea</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color: #f87171; font-size: 0.9rem; font-weight: 600;">○ Sistema Fuera de Línea</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    st.markdown("### 📊 Materia de Análisis")
    st.markdown("""
    <div class="sidebar-info">
    Este asistente está especializado en el <b>Presupuesto 2026</b> de la Diputación de Sevilla, incluyendo organismos autónomos y entidantes dependientes.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 💡 Sugerencias de análisis")
    with st.expander("Ver ejemplos de preguntas"):
        st.markdown("""
        - ¿Cuál es el gasto total en políticas sociales?
        - Resume la inversión prevista para Prodetur.
        - ¿Cuánto aumenta el presupuesto respecto a 2025?
        - ¿Cuáles son las mayores partidas de subvenciones?
        - Desglosa el presupuesto por capítulos.
        """)
    
    st.markdown("---")
    
    if st.button("🗑️ Nueva Conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.rerun()

    st.caption("v2.0 | IA Fiscal Diputación Sevilla")

# ============================================================================
# Chat Core
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de usuario
if prompt := st.chat_input("Consulta cualquier detalle sobre las cuentas de 2026..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Analizando fuentes presupuestarias..."):
            result = query_notebooklm(
                question=prompt,
                notebook_id=NOTEBOOK_ID,
                conversation_id=st.session_state.conversation_id
            )
            
            if result.get("success"):
                response = result.get("answer") or ""
                
                # Manejar respuestas vacías de forma explícita
                if not response.strip():
                    response = "⚠️ **El sistema no ha encontrado información específica en las fuentes para esta consulta.** Por favor, intenta reformular la pregunta o consultar sobre otro área del presupuesto."
                
                if result.get("conversation_id"):
                    st.session_state.conversation_id = result["conversation_id"]
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                error_msg = f"⚠️ **Error en la consulta:** {result.get('error')}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer flotante discreto
st.markdown(
    """
    <div style='position: fixed; bottom: 10px; right: 20px; color: rgba(255,255,255,0.3); font-size: 0.7rem;'>
        DipuBot 2026 Analysis System
    </div>
    """,
    unsafe_allow_html=True
)
