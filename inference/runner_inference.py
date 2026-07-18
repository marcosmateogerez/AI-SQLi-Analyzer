import logging
import os
import random
import re
import time

from google import genai
from google.genai import types

import config

# Configuración de Logging.
logger = logging.getLogger(f"app.{__name__}")

# Constantes de control de la API.
MAX_REINTENTOS = 3
ESPERA_BASE = 10
PAUSA_ENTRE_ESCENARIOS = 15


def limpiar_codigo_markdown(texto_crudo: str) -> str:
    """
    Extrae el código contenido en bloques markdown y retorna únicamente
    el contenido ejecutable.
    """
    patron = r"```python\s*(.*?)\s*```"
    resultado = re.search(patron, texto_crudo, re.DOTALL)
    return resultado.group(1).strip() if resultado else texto_crudo.strip()


def es_error_reintentable(e: Exception) -> bool:
    """
    Devuelve false para errores permanentes del cliente, y true para errores
    transitorios de red o del servidor.
    """
    mensaje = str(e).lower()
    errores_permanentes = {
        "400",
        "401",
        "403",
        "404",
        "invalid argument",
        "unauthenticated",
        "permission denied",
    }
    return not any(err in mensaje for err in errores_permanentes)


def generar_codigo_escenario(
    client: genai.Client,
    ruta_prompt: str,
    ruta_salida: str,
    gen_config: types.GenerateContentConfig,
) -> bool:
    """
    Maneja la lectura del prompt, el bucle de reintentos con backoff exponencial
    y el almacenamiento del código para un único escenario.
    """
    with open(ruta_prompt, "r", encoding="utf-8") as f:
        prompt_contenido = f.read()

    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            respuesta = client.models.generate_content(
                model=config.LLM_MODEL, contents=prompt_contenido, config=gen_config
            )
            texto_respuesta = respuesta.text

            if not texto_respuesta or not texto_respuesta.strip():
                raise ValueError("El modelo devolvió una respuesta vacía.")

            codigo_limpio = limpiar_codigo_markdown(texto_respuesta)

            with open(ruta_salida, "w", encoding="utf-8") as f:
                f.write(codigo_limpio)

            return True

        except Exception as e:
            if not es_error_reintentable(e):
                break

            if intento < MAX_REINTENTOS:
                tiempo_espera = ESPERA_BASE * (2 ** (intento - 1)) + random.uniform(
                    0, 3
                )
                time.sleep(tiempo_espera)

    return False


def ejecutar_inferencia_completa() -> None:
    """
    Función principal que gestiona las validaciones iniciales de entorno,
    escanea los directorios del dataset y coordina la inferencia completa.
    """
    logger.info("Fase 1: generación de código con el LLM.")

    if not config.GEMINI_API_KEY:
        logger.error("No se detectó la variable de entorno GEMINI_API_KEY.")
        return

    if not os.path.exists(config.DATASET_DIR):
        logger.error(f"La carpeta de dataset no existe en {config.DATASET_DIR}.")
        return

    # Inicialización del modelo.
    client = genai.Client(
        api_key=config.GEMINI_API_KEY, http_options=types.HttpOptions(timeout=120_000)
    )

    config_generacion = types.GenerateContentConfig(temperature=0.0, seed=42)

    # Procesamiento secuencial del dataset.
    for elemento in os.listdir(config.DATASET_DIR):
        ruta_escenario = os.path.join(config.DATASET_DIR, elemento)

        if not os.path.isdir(ruta_escenario):
            continue

        ruta_prompt = os.path.join(ruta_escenario, "prompt.txt")
        ruta_salida_codigo = os.path.join(ruta_escenario, "codigo_ia.py")

        if not os.path.exists(ruta_prompt):
            logger.warning(f"Saltando '{elemento}', no se encontró prompt.txt.")
            continue

        logger.info(f"Procesando {elemento}...")

        exito = generar_codigo_escenario(
            client, ruta_prompt, ruta_salida_codigo, config_generacion
        )

        if not exito:
            logger.warning(f"Escenario '{elemento}' omitido permanentemente.")

        time.sleep(PAUSA_ENTRE_ESCENARIOS)


if __name__ == "__main__":
    ejecutar_inferencia_completa()
