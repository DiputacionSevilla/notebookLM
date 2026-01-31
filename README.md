# 🤖 Chat NotebookLM - YouTube IA Strategy

Aplicación web desarrollada en Streamlit para interactuar mediante chat con el cuaderno de NotebookLM "Estrategia YouTube IA y Formación School".

## ✨ Características

- 💬 Interfaz de chat moderna y limpia
- 🔗 Conexión directa con NotebookLM vía MCP Server
- 📝 Historial de conversación persistente en la sesión
- ⚡ Indicadores de carga y manejo de errores
- 🎨 Diseño con gradientes y estilos premium

## 📋 Requisitos Previos

- Python 3.8 o superior
- Servidor MCP de NotebookLM configurado y autenticado
- Cuenta de NotebookLM con el cuaderno creado

## 🚀 Instalación

1. **Clonar o ubicar el proyecto:**
   ```bash
   cd c:\Users\carry\OneDrive\Documentos\Proyectos\notebooklm
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno (opcional):**
   ```bash
   # Copiar el archivo de ejemplo
   copy .env.example .env
   
   # Editar .env con tus valores
   ```

## 🎯 Uso

1. **Ejecutar la aplicación:**
   ```bash
   streamlit run app.py
   ```

2. **Abrir en el navegador:**
   - La aplicación se abrirá automáticamente en `http://localhost:8501`
   - Si no se abre, accede manualmente a la URL

3. **Interactuar con el chat:**
   - Escribe tus preguntas en el campo de entrada
   - Las respuestas provienen directamente del cuaderno NotebookLM
   - El historial se mantiene durante la sesión

## 🛠️ Configuración

### ID del Cuaderno NotebookLM

El ID del cuaderno está configurado en `app.py`:
```python
NOTEBOOK_ID = "8442d244-d797-48fe-b495-21d053e6ac4e"
```

### Servidor MCP

La aplicación utiliza el servidor MCP de NotebookLM que debe estar configurado en:
```
C:\Users\carry\.gemini\antigravity\mcp_config.json
```

## 💡 Ejemplos de Preguntas

- "¿Qué área de conocimiento tiene más futuro para emprender en IA?"
- "¿Cómo implementar un chatbot con RAG?"
- "Dame ideas de contenido para mi canal de YouTube sobre IA"
- "¿Qué herramientas de automatización recomiendas para escalar?"

## 🎨 Estructura del Proyecto

```
notebooklm/
├── app.py                 # Aplicación principal Streamlit
├── requirements.txt       # Dependencias de Python
├── README.md             # Este archivo
└── .env.example          # Plantilla de variables de entorno
```

## 🐛 Solución de Problemas

### Error: "No se puede conectar al servidor MCP"
- Verifica que el servidor MCP esté autenticado
- Ejecuta: `notebooklm-mcp-auth` en la terminal
- Reinicia la aplicación Streamlit

### Error: "Notebook not found"
- Verifica que el NOTEBOOK_ID sea correcto
- Comprueba que tienes acceso al cuaderno en NotebookLM

### La aplicación no se abre en el navegador
- Abre manualmente: `http://localhost:8501`
- Verifica que el puerto 8501 no esté ocupado
- Intenta con otro puerto: `streamlit run app.py --server.port 8502`

## 🔐 Seguridad

- Las credenciales de NotebookLM se gestionan a través del servidor MCP
- No se almacenan datos sensibles en el código
- El historial de chat se mantiene solo en memoria durante la sesión

## 📄 Licencia

Proyecto personal para gestión de conocimiento de estrategia YouTube IA.

## 🤝 Contribuciones

Este es un proyecto personal, pero puedes adaptarlo para tus propios cuadernos de NotebookLM.

---

**Desarrollado con ❤️ usando Streamlit y NotebookLM MCP Server**
