"""
Script para exportar tus cookies locales a formato de variable de entorno.
Ejecuta esto localmente y copia el resultado para pegarlo en la configuración de tu nube.
"""
import json
import os
from pathlib import Path

def get_auth_tokens():
    # Ruta por defecto donde se guardan los tokens en Windows
    auth_path = Path.home() / ".notebooklm-mcp" / "auth.json"
    
    if not auth_path.exists():
        print(f"❌ No se encontró el archivo de autenticación en: {auth_path}")
        print("Por favor ejecuta 'notebooklm-mcp-auth' primero.")
        return

    try:
        with open(auth_path, 'r') as f:
            data = json.load(f)
            
        cookies = data.get('cookies', {})
        
        # Convertir diccionario de cookies a string de cabecera (formato cookie1=valor1; cookie2=valor2)
        cookie_string = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        print("\n✅ COOKIES ENCONTRADAS EXITOSAMENTE")
        print("==================================================")
        print("Copia TODO el contenido entre las líneas punteadas y asígnalo")
        print("a la variable de entorno 'NOTEBOOKLM_COOKIES' en tu proveedor cloud.")
        print("==================================================\n")
        print("--- COPIAR DESDE AQUÍ ---")
        print(cookie_string)
        print("--- HASTA AQUÍ ---\n")
        
        print("ℹ️ IMPORTANTE: Estas cookies caducan eventualmente. Si la app deja de funcionar,")
        print("   tendrás que volver a extraerlas y actualizar la variable en la nube.")

    except Exception as e:
        print(f"❌ Error leyendo el archivo: {str(e)}")

if __name__ == "__main__":
    get_auth_tokens()
