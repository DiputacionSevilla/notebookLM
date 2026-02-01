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

# Estilos Institucionales (Paleta de colores claros)
def local_css():
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@500;700&display=swap" rel="stylesheet">
    
    <style>
        /* Base and Typography */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #334155;
        }
        
        h1, h2, h3 {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
        }

        /* Main Container Background (Claro) */
        .stApp {
            background-color: #f8fafc;
            background-image: 
                radial-gradient(at 0% 0%, rgba(0, 150, 94, 0.05) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(71, 85, 105, 0.05) 0px, transparent 50%);
        }

        /* Sidebar Styling (Gris oscuro Institucional) */
        section[data-testid="stSidebar"] {
            background-color: #334155;
            border-right: 3px solid #00965e;
        }
        
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
            color: white !important;
        }

        /* Chat Messages (Estilo institucional claro) */
        [data-testid="stChatMessage"] {
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }

        /* User Message specific style (Verde institucional muy suave) */
        [data-testid="stChatMessage"]:nth-child(even) {
            background-color: #f0fdf4;
            border: 1px solid #dcfce7;
        }

        /* Titles and Text (Tamaño mayor según petición) */
        .big-title {
            color: #334155;
            font-size: 4rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
            text-align: left;
            line-height: 1.1;
        }
        
        .subtitle {
            color: #00965e;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 2.5rem;
        }

        /* Custom widgets */
        .stButton>button {
            border-radius: 6px;
            font-weight: 600;
            background-color: #00965e !important;
            color: white !important;
            border: none;
            transition: all 0.2s ease;
        }
        
        .stButton>button:hover {
            background-color: #007a4d !important;
            transform: scale(1.02);
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

# Header adaptable
st.markdown('<p class="big-title">Chat con el presupuesto de la Dipu</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análisis inteligente del Presupuesto 2026 - Diputación de Sevilla</p>', unsafe_allow_html=True)

# Sidebar Premium
with st.sidebar:
    try:
        st.image("logo-dipu.png", width=220, use_container_width=False)
    except:
        st.markdown("🏛️ **Diputación de Sevilla**")
    st.markdown("## 🏛️ Gestión Presupuestaria")
    
    # Estado de la conexión
    health = check_api_health()
    if health.get("status") == "ok":
        st.markdown('<div style="color: #4ade80; font-size: 0.9rem;">● En línea | Motor IA Listo</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color: #f87171; font-size: 0.9rem;">○ Desconectado | Reinicia el túnel</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    st.markdown("### 📊 Contenido del Cuaderno")
    st.markdown("""
    Este asistente tiene acceso a los documentos oficiales del **Presupuesto 2026**:
    - Memoria de alcaldía
    - Estado de gastos e ingresos
    - Organismos autónomos (Prodetur, OPAEF, etc.)
    - Planes provinciales de inversión
    - Gastos de personal y subvenciones
    """)
    
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
                response = result.get("answer", "Sin respuesta disponible.")
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
