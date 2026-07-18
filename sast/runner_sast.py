import logging
import os
import subprocess
import sys

import config

# Configuración de Logging.
logger = logging.getLogger(f"app.{__name__}")

# Constantes de configuración.
CODIGO_IA_FILENAME = "codigo_ia.py"
REGLA_SQLI_BANDIT = "B608"


def analizar_escenario_con_bandit(
    elemento: str, ruta_codigo: str, ruta_reporte: str, env: dict[str, str]
) -> None:
    """
    Invoca el subproceso ejecutor de Bandit para un escenario específico
    y valida la correcta creación de su reporte JSON resultante.
    """
    comando = [
        sys.executable,
        "-m",
        "bandit",
        "--tests",
        REGLA_SQLI_BANDIT,
        "-f",
        "json",
        "-o",
        ruta_reporte,
        ruta_codigo,
    ]

    try:
        resultado = subprocess.run(
            comando, capture_output=True, encoding="utf-8", env=env
        )

        if resultado.returncode >= 2 or not os.path.exists(ruta_reporte):
            logger.error(f"Error en el escenario '{elemento}', no se pudo procesar.")

    except Exception:
        logger.error(f"Error inesperado en el escenario '{elemento}', no se procesó.")


def ejecutar_sast_completo() -> None:
    """
    Función principal que valida el entorno del dataset, recorre secuencialmente
    los escenarios y coordina la fase de análisis estático.
    """
    logger.info("Fase 2: análisis estático.")

    if not os.path.exists(config.DATASET_DIR):
        logger.error(f"La carpeta de dataset no existe en {config.DATASET_DIR}.")
        return

    os.makedirs(config.SAST_REPORTS_DIR, exist_ok=True)

    env_utf8 = os.environ.copy()
    env_utf8["PYTHONUTF8"] = "1"

    # Escaneo y procesamiento secuencial de directorios.
    for elemento in os.listdir(config.DATASET_DIR):
        ruta_escenario = os.path.join(config.DATASET_DIR, elemento)

        if not os.path.isdir(ruta_escenario):
            continue

        ruta_codigo = os.path.join(ruta_escenario, CODIGO_IA_FILENAME)
        if not os.path.exists(ruta_codigo):
            logger.warning(
                f"Saltando '{elemento}', no se encontró {CODIGO_IA_FILENAME}."
            )
            continue

        ruta_reporte = os.path.join(config.SAST_REPORTS_DIR, f"{elemento}_sast.json")

        logger.info(f"Procesando {elemento}...")

        analizar_escenario_con_bandit(elemento, ruta_codigo, ruta_reporte, env_utf8)


if __name__ == "__main__":
    ejecutar_sast_completo()
