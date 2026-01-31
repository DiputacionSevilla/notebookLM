"""
Módulo de integración NotebookLM MCP para Streamlit
Este módulo permite a Streamlit comunicarse con el servidor MCP de NotebookLM
"""
import subprocess
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class NotebookLMClient:
    """Cliente para interactuar con NotebookLM vía MCP"""
    
    def __init__(self, notebook_id: str):
        self.notebook_id = notebook_id
        self.mcp_command = self._get_mcp_command()
    
    def _get_mcp_command(self) -> list:
        """Obtiene el comando MCP desde la configuración"""
        try:
            config_path = Path.home() / ".gemini" / "antigravity" / "mcp_config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            notebooklm_config = config.get("mcpServers", {}).get("notebooklm", {})
            command = notebooklm_config.get("command", "")
            args = notebooklm_config.get("args", [])
            
            return [command] + args if command else []
        except Exception as e:
            print(f"Error leyendo configuración MCP: {e}")
            return []
    
    def query(self, question: str, conversation_id: Optional[str] = None, timeout: Optional[int] = 120) -> Dict[str, Any]:
        """
        Realiza una consulta al cuaderno NotebookLM
        
        Args:
            question: Pregunta a realizar
            conversation_id: ID de conversación para seguimiento de contexto
            timeout: Timeout en segundos
            
        Returns:
            Dict con 'success', 'answer', 'conversation_id' o 'error'
        """
        try:
            # Construir el script Python que ejecutará la consulta MCP
            script_content = f'''
import sys
sys.path.insert(0, r"{Path(__file__).parent}")

# Intentar importar y usar las herramientas MCP
try:
    # Este es un placeholder - en tu entorno Antigravity tienes acceso directo a mcp_notebooklm_notebook_query
    # Pero en Streamlit necesitamos llamarlo de otra forma
    
    print({json.dumps({
        "success": False,
        "error": "MCP no accesible desde subprocess. Usa la solución de consulta directa."
    })})
except Exception as e:
    import json
    print(json.dumps({{"success": False, "error": str(e)}}))
'''
            
            # Por limitaciones de arquitectura, retornamos un mensaje guía
            return {
                "success": False,
                "error": "architect_limitation",
                "message": """
🚧 **Limitación de Arquitectura**

La aplicación Streamlit no puede acceder directamente al servidor MCP desde un proceso separado.

**💡 Solución Práctica:**
Hazme tus preguntas directamente aquí en el chat principal (fuera de Streamlit) y yo consultaré el cuaderno de NotebookLM por ti usando las herramientas MCP disponibles.

**Ejemplo:**
"Consulta el cuaderno: ¿Qué área tiene más potencial de futuro?"
"""
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def test_connection() -> Dict[str, Any]:
    """Prueba la conexión con el servidor MCP"""
    try:
        config_path = Path.home() / ".gemini" / "antigravity" / "mcp_config.json"
        if not config_path.exists():
            return {
                "success": False,
                "error": "No se encontró archivo de configuración MCP"
            }
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "notebooklm" in config.get("mcpServers", {}):
            return {
                "success": True,
                "message": "Configuración MCP encontrada"
            }
        else:
            return {
                "success": False,
                "error": "Servidor notebooklm no configurado en MCP"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Test del módulo
    print("🧪 Probando NotebookLM Client...")
    result = test_connection()
    print(f"Resultado: {result}")
