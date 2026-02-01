# 🌐 Configuración de Cloudflare Tunnel

Este documento explica cómo configurar un túnel para que tu backend local sea accesible desde internet de forma permanente y gratuita.

## ¿Por qué usar un túnel?

Las cookies de Google caducan rápidamente cuando se usan desde una IP diferente a donde fueron creadas. Con el túnel:
- ✅ El backend corre en TU PC (misma IP que las cookies)
- ✅ Streamlit Cloud accede vía túnel
- ✅ Las cookies duran semanas/meses
- ✅ Auto-refresh funciona

## 📋 Requisitos Previos

1. Una cuenta de Cloudflare (gratis): https://dash.cloudflare.com/sign-up
2. Un dominio añadido a Cloudflare (puede ser gratis con Freenom o barato ~$10/año)

---

## 🚀 Instalación Paso a Paso

### Paso 1: Descargar cloudflared

```powershell
# Opción A: Con winget (recomendado)
winget install Cloudflare.cloudflared

# Opción B: Descarga manual
# Ir a: https://github.com/cloudflare/cloudflared/releases/latest
# Descargar: cloudflared-windows-amd64.exe
# Renombrar a: cloudflared.exe
# Mover a: C:\Program Files\cloudflared\
```

Verificar instalación:
```powershell
cloudflared --version
```

### Paso 2: Autenticar con Cloudflare

```powershell
cloudflared tunnel login
```

Se abrirá el navegador. Selecciona tu dominio y autoriza.

### Paso 3: Crear el túnel

```powershell
cloudflared tunnel create notebooklm-api
```

Anota el **UUID** que te devuelve (algo como `a1b2c3d4-e5f6-...`).

### Paso 4: Crear archivo de configuración

Crea el archivo `C:\Users\TU_USUARIO\.cloudflared\config.yml`:

```yaml
tunnel: TU-UUID-AQUI
credentials-file: C:\Users\TU_USUARIO\.cloudflared\TU-UUID-AQUI.json

ingress:
  - hostname: api.TU-DOMINIO.com
    service: http://localhost:8000
  - service: http_status:404
```

### Paso 5: Crear DNS en Cloudflare

```powershell
cloudflared tunnel route dns notebooklm-api api.TU-DOMINIO.com
```

### Paso 6: Iniciar el túnel

```powershell
cloudflared tunnel run notebooklm-api
```

---

## 🔧 Script de Inicio Automático

Usa el script `start_tunnel.bat` incluido en el proyecto para iniciar todo con un clic:
- Backend FastAPI
- Túnel Cloudflare
- (Opcional) Frontend Streamlit

---

## ✅ Actualizar Streamlit Cloud

Una vez el túnel funcione, actualiza los secrets de Streamlit Cloud:

```toml
API_BASE_URL = "https://api.TU-DOMINIO.com"
```

---

## 🐛 Solución de Problemas

| Problema | Solución |
|----------|----------|
| "tunnel not found" | Asegúrate de haber creado el túnel con `cloudflared tunnel create` |
| "credentials file not found" | Verifica la ruta en config.yml |
| No se conecta | Verifica que el backend esté corriendo en puerto 8000 |

---

## 📝 Resumen Rápido

```
1. cloudflared tunnel login                    # Una sola vez
2. cloudflared tunnel create notebooklm-api   # Una sola vez
3. cloudflared tunnel route dns ...           # Una sola vez
4. start_tunnel.bat                           # Cada vez que inicies
```
