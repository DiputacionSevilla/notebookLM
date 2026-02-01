# 🌐 Guía Completa: Configurar Túnel Cloudflare

Esta guía explica paso a paso cómo configurar un túnel desde tu PC local para exponer el backend de NotebookLM a internet, usando un dominio de IONOS.

---

## 📋 Requisitos

- Windows 10/11
- Dominio en IONOS (ej: `carrysoft.com`)
- Cuenta de Cloudflare (gratis)
- PowerShell

---

## 🎯 Resultado Final

```
Tu PC (FastAPI en localhost:8000)
       ↓ túnel cifrado
Cloudflare (notebooklm.carrysoft.com)
       ↓
Streamlit Cloud (accede a tu API)
```

---

## PARTE 1: Preparar Cloudflare

### Paso 1.1: Crear cuenta en Cloudflare

1. Ve a https://dash.cloudflare.com/sign-up
2. Crea cuenta con tu email
3. Verifica el email

### Paso 1.2: Añadir tu dominio a Cloudflare

1. En el dashboard, clic en **"+ Add a Site"**
2. Escribe tu dominio: `carrysoft.com` (sin www, sin subdominio)
3. Clic en **Continue**
4. Selecciona plan **Free** → Continue
5. Cloudflare escaneará tus DNS actuales (espera ~30 segundos)
6. Clic en **Continue** (puedes revisar los DNS después)

### Paso 1.3: Obtener los Nameservers de Cloudflare

Cloudflare te mostrará dos nameservers, algo como:
```
ada.ns.cloudflare.com
bob.ns.cloudflare.com
```

**¡COPIA ESTOS DOS VALORES!** Los necesitarás en el siguiente paso.

---

## PARTE 2: Configurar IONOS

### Paso 2.1: Acceder a la gestión de DNS

1. Ve a https://my.ionos.es/
2. Inicia sesión
3. Ve a **Dominios y SSL** → **carrysoft.com**
4. Busca **Servidores DNS** o **Nameservers**

### Paso 2.2: Cambiar los Nameservers

1. Selecciona **"Usar otros nameservers"** (o similar)
2. Elimina los nameservers actuales de IONOS
3. Añade los dos de Cloudflare:
   - `ada.ns.cloudflare.com`
   - `bob.ns.cloudflare.com`
4. Guarda los cambios

### Paso 2.3: Esperar propagación

- ⏱️ Puede tardar de **10 minutos a 24 horas** (normalmente ~1 hora)
- Cloudflare te enviará un email cuando el dominio esté activo
- También puedes verificar en el dashboard de Cloudflare (cambiará de "Pending" a "Active")

---

## PARTE 3: Instalar Cloudflared

### Paso 3.1: Instalar con winget

Abre **PowerShell como Administrador** y ejecuta:

```powershell
winget install Cloudflare.cloudflared
```

### Paso 3.2: ⚠️ IMPORTANTE - Reiniciar PowerShell

Después de instalar, **CIERRA PowerShell y ábrelo de nuevo**. 

Esto es necesario para que el sistema reconozca el nuevo comando.

### Paso 3.3: Verificar instalación

En la nueva ventana de PowerShell:

```powershell
cloudflared --version
```

Deberías ver algo como: `cloudflared version 2025.8.1`

---

## PARTE 4: Crear el Túnel

### Paso 4.1: Autenticar con Cloudflare

```powershell
cloudflared tunnel login
```

- Se abrirá tu navegador
- Selecciona el dominio `carrysoft.com`
- Clic en **Authorize**
- Vuelve a PowerShell (verás un mensaje de éxito)

Esto crea un certificado en: `C:\Users\TU_USUARIO\.cloudflared\cert.pem`

### Paso 4.2: Crear el túnel

```powershell
cloudflared tunnel create notebooklm-api
```

**IMPORTANTE:** Anota el **UUID** que te devuelve (algo como `a1b2c3d4-e5f6-7890-abcd-1234567890ab`).

Esto crea un archivo de credenciales en: `C:\Users\TU_USUARIO\.cloudflared\<UUID>.json`

### Paso 4.3: Crear el registro DNS

```powershell
cloudflared tunnel route dns notebooklm-api notebooklm.carrysoft.com
```

Esto crea automáticamente el subdominio en Cloudflare (no necesitas hacerlo manualmente).

---

## PARTE 5: Configurar el Túnel

### Paso 5.1: Crear archivo de configuración

Crea el archivo `C:\Users\TU_USUARIO\.cloudflared\config.yml` con el siguiente contenido:

```yaml
tunnel: PEGA-TU-UUID-AQUI
credentials-file: C:\Users\TU_USUARIO\.cloudflared\PEGA-TU-UUID-AQUI.json

ingress:
  - hostname: notebooklm.carrysoft.com
    service: http://localhost:8000
  - service: http_status:404
```

**Reemplaza:**
- `PEGA-TU-UUID-AQUI` → El UUID que anotaste en el paso 4.2
- `TU_USUARIO` → Tu nombre de usuario de Windows

---

## PARTE 6: Probar Todo

### Paso 6.1: Iniciar el backend

En una terminal:
```powershell
cd c:\Users\carry\OneDrive\Documentos\Proyectos\notebooklm
python api_server.py
```

### Paso 6.2: Iniciar el túnel

En OTRA terminal:
```powershell
cloudflared tunnel run notebooklm-api
```

### Paso 6.3: Verificar

Abre en tu navegador:
```
https://notebooklm.carrysoft.com/health
```

Deberías ver:
```json
{"status":"ok","message":"Servidor funcionando correctamente","authenticated":true}
```

---

## PARTE 7: Actualizar Streamlit Cloud

### Paso 7.1: Cambiar la URL de la API

1. Ve a https://share.streamlit.io
2. Selecciona tu app
3. Ve a **Settings** → **Secrets**
4. Cambia:

```toml
API_BASE_URL = "https://notebooklm.carrysoft.com"
```

5. Guarda y espera a que se redespliegue (~1 minuto)

---

## PARTE 8: Uso Diario

### Iniciar todo (cada vez que enciendas el PC):

Usa el script `start_tunnel.bat` o manualmente:

```powershell
# Terminal 1: Backend
python api_server.py

# Terminal 2: Túnel
cloudflared tunnel run notebooklm-api
```

### Renovar autenticación NotebookLM (cada 2-4 semanas):

```powershell
notebooklm-mcp-auth
```

Solo esto. Ya no necesitas exportar cookies ni actualizar Render.

---

## 🐛 Solución de Problemas

| Problema | Solución |
|----------|----------|
| `cloudflared` no se reconoce | Cierra y abre PowerShell de nuevo |
| "tunnel not found" | Ejecuta `cloudflared tunnel create notebooklm-api` |
| "hostname not found" | Espera a que Cloudflare active el dominio |
| Error 502 en navegador | El backend no está corriendo en localhost:8000 |
| Error de certificado | Ejecuta `cloudflared tunnel login` de nuevo |

---

## 📝 Resumen de Comandos

```powershell
# Solo la primera vez:
winget install Cloudflare.cloudflared    # Instalar
cloudflared tunnel login                  # Autenticar
cloudflared tunnel create notebooklm-api  # Crear túnel
cloudflared tunnel route dns notebooklm-api notebooklm.carrysoft.com  # DNS

# Cada día:
python api_server.py                      # Terminal 1
cloudflared tunnel run notebooklm-api     # Terminal 2

# Cada 2-4 semanas:
notebooklm-mcp-auth                       # Renovar cookies
```

---

## 📁 Archivos Importantes

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| Certificado Cloudflare | `~/.cloudflared/cert.pem` | Autenticación con Cloudflare |
| Credenciales del túnel | `~/.cloudflared/<UUID>.json` | Identidad del túnel |
| Configuración | `~/.cloudflared/config.yml` | Rutas del túnel |
| Cookies NotebookLM | `~/.notebooklm_mcp/auth.json` | Sesión de Google |

---

*Última actualización: Febrero 2026*
