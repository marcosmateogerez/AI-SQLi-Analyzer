from google.genai import types
from google import genai
import logging
import random
import config
import time
import os
import re

# Instanciación de logger para este módulo específico.
logger = logging.getLogger(f"app.{__name__}")

def limpiar_codigo_markdown(texto_crudo):
    """
    Extrae el código contenido en bloques markdown y retorna únicamente
    el contenido ejecutable.
    """
    patron = r"```python\s*(.*?)\s*```"
    resultado = re.search(patron, texto_crudo, re.DOTALL)
    if resultado:
        return resultado.group(1).strip()
    return texto_crudo.strip()

def es_error_reintentable(e):
    """
    Devuelve false para errores permanentes del cliente, y true para errores
    transitorios de red o del servidor.
    """
    mensaje = str(e).lower()
    errores_permanentes = ["400", "401", "403", "404", "invalid argument",
                           "unauthenticated", "permission denied"]
    if any(ind in mensaje for ind in errores_permanentes):
        return False
    return True

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
    client = genai.Client(
        api_key=config.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=120_000)
    )
    
    # Configuración para la replicabilidad (temperatura en cero y semilla fija).
    config_generacion = types.GenerateContentConfig(
        temperature=0.0,
        seed=42
    )

    # Verificación de la existencia de la carpeta del dataset antes de iniciar el proceso.
    if not os.path.exists(config.DATASET_DIR):
        logger.error(f"La carpeta de dataset no existe en {config.DATASET_DIR}.")
        return

    # Parámetros para el mecanismo de reintentos en caso de fallos en la llamada a la API del LLM.
    MAX_REINTENTOS = 3
    ESPERA_BASE = 10
    PAUSA_ENTRE_ESCENARIOS = 15

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

            # Control de éxito para el escenario actual.
            completado_con_exito = False

            # Bucle de reintentos para el escenario actual.
            for intento in range(1, MAX_REINTENTOS + 1):
                try:
                    respuesta = client.models.generate_content(
                        model=config.LLM_MODEL,
                        contents=prompt_contenido,
                        config=config_generacion
                    )
                    texto_respuesta = respuesta.text

                    # Verificación de que la respuesta no sea vacía antes de continuar.
                    if not texto_respuesta or not texto_respuesta.strip():
                        raise ValueError("El modelo devolvió una respuesta vacía.")

                    codigo_limpio = limpiar_codigo_markdown(texto_respuesta)

                    with open(ruta_salida_codigo, "w", encoding="utf-8") as f:
                        f.write(codigo_limpio)
                    
                    completado_con_exito = True
                    break

                except Exception as e:
                    # Verificación del tipo de error para determinar si vale la pena reintentar.
                    if not es_error_reintentable(e):
                        logger.error(f"Error permanente en {elemento}, no se reintentará: {e}")
                        break

                    logger.error(f"Fallo en intento {intento} para {elemento}: {e}")
                    if intento < MAX_REINTENTOS:
                        # Backoff exponencial con jitter para espaciar los reintentos.
                        tiempo_espera = ESPERA_BASE * (2 ** (intento - 1)) + random.uniform(0, 3)
                        logger.info(f"Reintentando en {tiempo_espera:.1f}s...")
                        time.sleep(tiempo_espera)

            # Si el escenario falló todos los reintentos, continúa con el siguiente del dataset.
            if not completado_con_exito:
                logger.warning(f"Escenario {elemento} omitido por fallas consecutivas en la API.")

            # Pausa entre escenarios para respetar el RPM.
            time.sleep(PAUSA_ENTRE_ESCENARIOS)

if __name__ == "__main__":
    ejecutar_inferencia_completa()