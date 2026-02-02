# Alternativa: Migrar a Gemini API con File Search

> Documento de referencia para futura migracion del sistema.
> Fecha de estudio: 2026-02-02

## Problema actual con NotebookLM

- NotebookLM no tiene API oficial publica
- La autenticacion usa cookies de Google que caducan rapidamente
- En entornos corporativos con proxy (Fortinet), las sesiones se invalidan aun mas rapido
- Requiere renovacion manual de cookies frecuentemente

---

## Solucion propuesta: Gemini API File Search Tool

Google lanzo el **File Search Tool**, un sistema RAG integrado directamente en la API de Gemini que funciona de forma muy similar a NotebookLM pero con autenticacion robusta.

### Ventajas principales

| Caracteristica | NotebookLM (actual) | Gemini File Search |
|----------------|---------------------|-------------------|
| Autenticacion | Cookies Google (caducan) | **API Key (permanente)** |
| Proxy corporativo | Problemas frecuentes | Sin problemas |
| RAG automatico | Si | Si |
| Citaciones | Si | Si |
| API oficial | No | **Si** |
| Coste | Gratis | Gratis (almacenamiento) + coste por consulta |

### Caracteristicas del File Search Tool

- **Sistema RAG gestionado**: Google maneja automaticamente el chunking, embeddings y retrieval
- **Formatos soportados**: PDF, DOCX, TXT, JSON, archivos de codigo
- **Almacenamiento gratuito**: El storage y generacion de embeddings son gratis
- **Citaciones automaticas**: Las respuestas incluyen referencias a los documentos fuente
- **Busqueda semantica**: Entiende el contexto, no solo palabras clave
- **Multi-hop retrieval**: Puede hacer consultas complejas que requieren multiples busquedas

---

## Como funciona

1. **Crear un File Search Store**: Contenedor para tus documentos
2. **Subir documentos**: PDFs del presupuesto
3. **Gemini genera embeddings**: Automaticamente, sin coste
4. **Hacer consultas**: Usando la API generateContent con el tool de File Search
5. **Recibir respuestas**: Con citas a los documentos fuente

---

## Implementacion

### Prerequisitos

1. Cuenta en Google AI Studio: https://aistudio.google.com
2. API Key gratuita
3. Instalar SDK: `pip install google-genai`

### Codigo de ejemplo

```python
from google import genai

# Inicializar cliente con API Key
client = genai.Client(api_key="TU_API_KEY")

# Crear un File Search Store
store = client.file_search_stores.create(
    name="Presupuesto-Diputacion-Sevilla-2026"
)

# Subir documentos
client.file_search_stores.upload_file(
    store_id=store.id,
    file_path="presupuesto_2026.pdf"
)

# Hacer una consulta con RAG
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Cual es el presupuesto total para 2026?",
    tools=[{
        "file_search": {
            "file_search_store": store.id
        }
    }]
)

print(response.text)
# La respuesta incluye citas automaticas a los documentos
```

### Estructura propuesta para migracion

```
api_server.py (modificado)
    |
    +-- Inicializar cliente Gemini con API Key
    |
    +-- Endpoint /query
    |       |
    |       +-- Usar file_search tool
    |       +-- Retornar respuesta con citas
    |
    +-- Endpoint /upload (nuevo, opcional)
            |
            +-- Subir nuevos documentos al store
```

---

## Limites y consideraciones

### File Search Tool
- Ideal para decenas o cientos de documentos
- Almacenamiento y embeddings gratuitos
- Coste solo por consultas (tokens de entrada/salida)

### Files API directa (alternativa para pocos docs)
- Limite: 50MB o 1000 paginas por PDF
- Archivos expiran en 48 horas
- Mejor para 5-10 documentos pequenos
- Sin coste de almacenamiento

### Vertex AI RAG Engine (alternativa enterprise)
- Para proyectos en Google Cloud
- Autenticacion con Service Accounts
- Mas control y personalizacion
- Requiere proyecto de Google Cloud

---

## Enlaces de documentacion

- File Search Tool (Blog oficial): https://blog.google/innovation-and-ai/technology/developers-tools/file-search-gemini-api/
- File Search Documentation: https://ai.google.dev/gemini-api/docs/file-search
- Files API: https://ai.google.dev/gemini-api/docs/files
- Document Processing: https://ai.google.dev/gemini-api/docs/document-processing
- Google AI Studio: https://aistudio.google.com
- Tutorial DataCamp: https://www.datacamp.com/tutorial/google-file-search-tool
- Ejemplo RAG con File Search: https://medium.com/google-cloud/rag-just-got-much-easier-with-file-search-tool-in-gemini-api-6494f5b1c6bc

---

## Pasos para migrar

1. [ ] Crear cuenta en Google AI Studio
2. [ ] Obtener API Key
3. [ ] Probar subiendo un PDF del presupuesto manualmente
4. [ ] Verificar que las respuestas son correctas y con citas
5. [ ] Modificar api_server.py para usar Gemini API
6. [ ] Actualizar app.py si es necesario
7. [ ] Probar en entorno corporativo con proxy
8. [ ] Documentar el proceso

---

## Notas adicionales

- El File Search Tool **no soporta Vertex AI**, solo Gemini API con API Key
- Los archivos en el File Search Store son persistentes (no expiran como en Files API)
- Se puede tener multiples stores para diferentes proyectos/temas
- Las instrucciones del sistema (responder en castellano, etc.) se pueden incluir en el prompt

---

*Documento generado durante sesion de trabajo - Febrero 2026*
