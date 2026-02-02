# 🏛️ DipuBot 2026: Análisis del Presupuesto de la Diputación de Sevilla

Asistente inteligente basado en **NotebookLM** para navegar y analizar los presupuestos 2026 de la Diputación de Sevilla y sus organismos autónomos.

## ✨ Características Premium
- **Análisis Profundo**: Respuestas basadas únicamente en fuentes oficiales (memorias, estados contables, planes provinciales).
- **Interfaz Moderna**: Diseño premium con Glassmorphism y tipografía optimizada.
- **Arquitectura Estable**: Túnel Cloudflare para mantener la autenticación persistente con Google.
- **Precisión IA**: Configurada para no inventar información y responder siempre en castellano.

## 📋 Arquitectura

```
┌─────────────────┐     HTTP      ┌─────────────────┐     API      ┌─────────────────┐
│   Streamlit     │ ───────────→  │    FastAPI      │ ──────────→  │   NotebookLM    │
│   (Frontend)    │               │   (Backend)     │              │   (Google)      │
│   Puerto 8501   │  ← ───────────│   Puerto 8000   │ ← ──────────│                 │
└─────────────────┘               └─────────────────┘              └─────────────────┘
```

## 🗂️ Estructura del Proyecto

```
notebooklm/
├── app.py              # Frontend Streamlit (interfaz de chat)
├── api_server.py       # Backend FastAPI (puente a NotebookLM)
├── export_cookies.py   # Script para exportar cookies a la nube
├── debug_query.py      # Script de diagnóstico
├── start.bat           # Script para iniciar ambos servidores (Windows)
├── requirements.txt    # Dependencias Python
├── Dockerfile          # Configuración Docker para despliegue
├── .gitignore          # Archivos a ignorar en Git
└── README.md           # Este archivo
```

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.11+
- Cuenta de Google con acceso a NotebookLM
- Git

### Instalación Local

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/notebookLM.git
cd notebookLM

# 2. Crear entorno virtual (recomendado)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Autenticarse con NotebookLM (primera vez)
notebooklm-mcp-auth
```

### Ejecutar en Local

**Opción A - Script automático (Windows):**
```bash
start.bat
```

**Opción B - Manual:**
```bash
# Terminal 1: Backend
python api_server.py

# Terminal 2: Frontend
streamlit run app.py
```

Abre http://localhost:8501 en tu navegador.

## ☁️ Despliegue en la Nube

### Backend (Render)

1. **Crear nuevo Web Service** en [render.com](https://render.com)
2. **Conectar repositorio** de GitHub
3. **Configurar:**
   - Environment: `Docker`
   - Branch: `main`
4. **Agregar variable de entorno:**
   - Key: `NOTEBOOKLM_COOKIES`
   - Value: *(ejecuta `python export_cookies.py` y copia el resultado)*

### Frontend (Streamlit Cloud)

1. **Ir a** [share.streamlit.io](https://share.streamlit.io)
2. **Conectar repositorio** de GitHub
3. **Configurar secrets** (Advanced settings):
   ```toml
   API_BASE_URL = "https://TU-SERVICIO.onrender.com"
   ```

## 🔧 Mantenimiento

### Renovar Autenticación (cuando caduquen las cookies)

Las cookies de Google duran aproximadamente **1-3 semanas**. Si la app deja de funcionar:

```bash
# 1. Ejecutar en tu PC local
notebooklm-mcp-auth

# 2. Exportar las nuevas cookies
python export_cookies.py

# 3. Copiar el resultado y actualizar en Render:
#    Dashboard → Tu servicio → Environment → NOTEBOOKLM_COOKIES
```

### Cambiar el Cuaderno de NotebookLM

Edita `app.py` línea 25:
```python
NOTEBOOK_ID = "tu-nuevo-notebook-id"
```

El ID se encuentra en la URL de NotebookLM: `https://notebooklm.google.com/notebook/ESTE-ES-EL-ID`

## 📡 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado del servidor y autenticación |
| POST | `/query` | Realizar consulta al cuaderno |
| GET | `/notebooks` | Listar cuadernos disponibles |
| POST | `/refresh-auth` | Intentar refrescar autenticación |

### Ejemplo de Consulta

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Cuál es la estrategia principal?",
    "notebook_id": "0523ea1e-7973-400a-a749-55a805205030"
  }'
```

## 🛡️ Características de Estabilidad

-   **Auto-retry:** Si falla la autenticación, reintenta automáticamente
-   **Lazy Initialization:** El cliente se inicializa bajo demanda
-   **Headless Auth Recovery:** Intenta refrescar tokens automáticamente (solo local)
-   **Error Handling:** Captura específica de errores HTTP 400/500

## 🔐 Seguridad

- Las cookies **nunca** se suben a Git (`.gitignore`)
- En producción, usa variables de entorno para secretos
- El archivo `auth.json` local está excluido del repositorio

## 📦 Dependencias Principales

- `fastapi` - Framework backend
- `uvicorn` - Servidor ASGI
- `streamlit` - Framework frontend
- `notebooklm-mcp-server` - Cliente de NotebookLM
- `httpx` - Cliente HTTP asíncrono
- `requests` - Cliente HTTP (frontend)

## 🐛 Solución de Problemas

| Problema | Solución |
|----------|----------|
| "API no autenticada" | Ejecuta `notebooklm-mcp-auth` |
| "Error 400 Bad Request" | Renueva cookies con `export_cookies.py` |
| "Conexión rechazada" | Verifica que `api_server.py` esté corriendo |
| Nube no funciona | Actualiza `NOTEBOOKLM_COOKIES` en Render |

## 📄 Licencia

Proyecto personal para uso educativo.

---

*Última actualización: Enero 2026*
