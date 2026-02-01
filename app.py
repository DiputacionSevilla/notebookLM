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
        API_BASE_URL = "http://localhost:8000"
except Exception:
    API_BASE_URL = "http://localhost:8000"

# ID del cuaderno (Actualizado para el nuevo contexto si es necesario, 
# por ahora mantenemos el ID pero el usuario indicó que el contenido cambió)
NOTEBOOK_ID = "8442d244-d797-48fe-b495-21d053e6ac4e"

# ============================================================================
# Configuración de la página
# ============================================================================

st.set_page_config(
    page_title="Presupuesto 2026 - Dipu Sevilla",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos Institucionales Premium (Modo Oscuro Elegante)
def local_css():
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@500;700&display=swap" rel="stylesheet">
    
    <style>
        /* Base and Typography */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3 {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
        }

        /* Main Container Background (Modo Oscuro Premium) */
        .stApp {
            background-color: #0f172a;
            background-image: 
                radial-gradient(at 0% 0%, rgba(0, 150, 94, 0.1) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(30, 41, 59, 0.1) 0px, transparent 50%);
        }

        /* Banner Superior Institucional */
        .header-banner {
            background-color: #1e293b;
            padding: 1.5rem 2rem;
            margin: -6rem -5rem 2.5rem -5rem;
            border-bottom: 3px solid #22c55e;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
        }
        
        .header-banner h1 {
            color: #ffffff;
            font-size: 2.2rem !important;
            margin: 0;
            letter-spacing: -1px;
        }

        /* Sidebar Styling (Vidrio Oscuro) */
        section[data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.8) !important;
            backdrop-filter: blur(12px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {
            color: #cbd5e1 !important;
        }

        /* Chat Messages (Glassmorphism Premium) */
        [data-testid="stChatMessage"] {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            backdrop-filter: blur(8px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        }

        /* User Message specific style */
        [data-testid="stChatMessage"]:nth-child(even) {
            background-color: rgba(34, 197, 94, 0.1);
            border: 1px solid rgba(34, 197, 94, 0.2);
        }

        /* Message text color */
        [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {
            color: #f8fafc !important;
            line-height: 1.6;
        }

        /* Custom widgets */
        .stButton>button {
            border-radius: 6px;
            font-weight: 600;
            background-color: #22c55e !important;
            color: white !important;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: #16a34a !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
        }

        /* Sidebar info box */
        .sidebar-info {
            background-color: rgba(255,255,255,0.03);
            padding: 1rem;
            border-radius: 8px;
            border-left: 3px solid #22c55e;
            margin-bottom: 1rem;
        }

        /* Hide Streamlit elements */
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
        payload = {
            "question": question,
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

# Header Institucional
st.markdown('<div class="header-banner"><h1>Chat con el presupuesto de la Dipu</h1></div>', unsafe_allow_html=True)
st.markdown('<p style="color: #64748b; font-weight: 600; margin-top: 10px;">📊 Análisis inteligente del Presupuesto 2026 - Diputación de Sevilla</p>', unsafe_allow_html=True)

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
