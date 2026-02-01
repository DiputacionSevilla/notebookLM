# 🔑 Guía de Renovación de Credenciales

## ¿Cuándo necesito renovar las credenciales?

Las cookies de autenticación de Google caducan aproximadamente cada **1-3 semanas**. Sabrás que han caducado cuando:

- ❌ La app en la nube muestra "API activa pero no autenticada"
- ❌ Las consultas devuelven "Error de autenticación"
- ❌ Recibes errores 401 o 400 en los logs de Render

---

## 📋 Proceso Paso a Paso (Modo Túnel)

### Paso 1: Iniciar el Sistema (Cada vez que enciendas el PC)

Ejecuta el script:
```powershell
./start_tunnel.bat
```
Esto abrirá dos ventanas: una para el backend FastAPI y otra para el túnel de Cloudflare.

---

### Paso 2: Generar Nuevas Credenciales (Solo si caducan)

Abre una terminal en la carpeta del proyecto y ejecuta:

```powershell
notebooklm-mcp-auth
```

**¿Qué sucede?**
- Se abrirá una ventana de Chrome
- Si no estás logueado, inicia sesión con tu cuenta de Google
- El script capturará las cookies automáticamente
- Verás un mensaje de "SUCCESS!" cuando termine

---

### Paso 2: Exportar las Cookies

En la misma terminal, ejecuta:

```powershell
python export_cookies.py
```

**Resultado esperado:**
```
✅ COOKIES ENCONTRADAS EXITOSAMENTE
==================================================
--- COPIAR DESDE AQUÍ ---
__Secure-3PSIDCC=AKEyXzVlqg....(texto muy largo)....
--- HASTA AQUÍ ---
```

⚠️ **IMPORTANTE:** Copia TODO el texto entre las líneas punteadas (es una sola línea muy larga).

---

### Paso 3: Actualizar en Render

1. **Ir a Render Dashboard:** https://dashboard.render.com

2. **Seleccionar tu servicio** (el backend de NotebookLM)

3. **Ir a "Environment"** en el menú lateral

4. **Buscar la variable `NOTEBOOKLM_COOKIES`**

5. **Hacer clic en "Edit"** (icono de lápiz)

6. **Borrar el valor antiguo** y **pegar el nuevo** (el texto que copiaste)

7. **Hacer clic en "Save Changes"**

---

### Paso 4: Esperar el Redespliegue

- Render reiniciará automáticamente tu servicio
- Espera **1-2 minutos** hasta que el estado sea "Live"
- Puedes ver el progreso en la pestaña "Events"

---

### Paso 5: Verificar

1. **Refresca** tu aplicación de Streamlit Cloud (F5)

2. **Mira el sidebar:**
   - ✅ Debe decir "Conectado a NotebookLM"
   - ❌ Si dice "API activa pero no autenticada", espera un poco más

3. **Haz una pregunta de prueba** para confirmar que funciona

---

## ⏰ Recordatorio Automático (Opcional)

Para no olvidar renovar las credenciales, puedes:

### Opción A: Alarma en el calendario
- Pon una alarma cada **2 semanas** para renovar credenciales

### Opción B: Monitoreo
- Configura una alerta en Render si el servicio devuelve errores 401

---

## 🐛 Solución de Problemas

| Síntoma | Causa Probable | Solución |
|---------|----------------|----------|
| `notebooklm-mcp-auth` no abre Chrome | Chrome no instalado o path incorrecto | Instala Chrome o configura la variable de entorno |
| "No se encontraron cookies" | No iniciaste sesión en Chrome | Ejecuta `notebooklm-mcp-auth` de nuevo e inicia sesión |
| Render no se actualiza | Caché de Render | Haz un "Manual Deploy" desde el dashboard |
| Sigue sin funcionar después de actualizar | Las cookies se copiaron mal | Asegúrate de copiar TODO el texto sin espacios extra |

---

## 📝 Resumen Rápido

```
1. notebooklm-mcp-auth          # Generar nuevas credenciales
2. python export_cookies.py      # Exportar para la nube
3. Copiar → Render → Environment → NOTEBOOKLM_COOKIES → Pegar → Save
4. Esperar 1-2 minutos
5. Probar en la app
```

---

*Este proceso tomará aproximadamente 2-3 minutos una vez que te acostumbres.*
