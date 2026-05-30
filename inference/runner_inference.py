from google.genai import types
from google import genai
import logging
import sys
import os
import re

# Inyección de la raíz del proyecto en el path del sistema para importar config.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Instanciación de logger para este módulo específico.
logger = logging.getLogger(f"app.{__name__}")

def limpiar_codigo_markdown(texto_crudo):
    """
    Extrae el código contenido en bloques markdown y retorna únicamente
    el contenido ejecutable.
    
    Parámetros:
        texto_crudo (str): texto posiblemente envuelto en un bloque
        markdown de Python.

    Retorno:
        str: código limpio y listo para ser ejecutado. Si no se detecta
        un bloque Markdown válido, se devuelve el texto original.
    """
    patron = r"```python\s*(.*?)\s*```"
    resultado = re.search(patron, texto_crudo, re.DOTALL)
    if resultado:
        return resultado.group(1).strip()
    return texto_crudo.strip()

def ejecutar_inferencia_completa():
    """
    Función principal que ejecuta el proceso completo de inferencia,
    configura el cliente del LLM, itera sobre los casos de uso en el dataset,
    y genera código utilizando el LLM y lo guarda en archivos específicos.
    """
    logger.info("Fase 1: generación de código con el LLM...")
        
    # Verificación de la clave API antes de proceder.
    if not config.GEMINI_API_KEY:
        logger.error("No se detectó la variable de entorno GEMINI_API_KEY.")
        return

    # Inicialización del cliente del LLM.
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    # Configuración para la replicabilidad (temperatura en cero y semilla fija).
    config_generacion = types.GenerateContentConfig(
        temperature=0.0,
        seed=42
    )

    # Verificación de la existencia de la carpeta del dataset antes de iniciar el proceso.
    if not os.path.exists(config.DATASET_DIR):
        logger.error(f"La carpeta de dataset no existe en {config.DATASET_DIR}.")
        return

    # Escaneo secuencial de los casos de uso en el dataset.
    for elemento in os.listdir(config.DATASET_DIR):
        ruta_escenario = os.path.join(config.DATASET_DIR, elemento)
        if os.path.isdir(ruta_escenario):
            ruta_prompt = os.path.join(ruta_escenario, "prompt.txt")
            ruta_salida_codigo = os.path.join(ruta_escenario, "codigo_ia.py")

            # Verificación de la existencia del archivo de prompt para el caso de uso actual.
            if not os.path.exists(ruta_prompt):
                logger.warning(f"El archivo de prompt no existe en {ruta_prompt}.")
                continue

            # Lectura del contenido del prompt para el caso de uso actual.
            with open(ruta_prompt, "r", encoding="utf-8") as f:
                prompt_contenido = f.read()

            # Generación del código utilizando el LLM.
            try:
                respuesta = client.models.generate_content(
                    model=config.LLM_MODEL,
                    contents=prompt_contenido,
                    config=config_generacion
                )
                texto_respuesta = respuesta.text

                codigo_limpio = limpiar_codigo_markdown(texto_respuesta)

                with open(ruta_salida_codigo, "w", encoding="utf-8") as f:
                    f.write(codigo_limpio)

            except Exception as e:
                logger.error(f"Error al procesar {elemento}: {e}")

if __name__ == "__main__":
    ejecutar_inferencia_completa()