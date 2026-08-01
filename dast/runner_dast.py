import logging
import os
import subprocess
import sys
import time

import psycopg2

import config

# Configuración de Logging.
logger = logging.getLogger(f"app.{__name__}")

# Constantes globales del módulo.
CODIGO_IA_FILENAME = "codigo_ia.py"
TARGET_URL = "http://127.0.0.1:5000"
TIEMPO_ESPERA_SERVIDOR = 5


def resetear_base_de_datos() -> None:
    """
    Elimina y recrea el esquema público de PostgreSQL para garantizar
    que cada escenario comience con una base de datos limpia.
    """
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="admin",
            dbname="test_db",
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA public CASCADE;")
            cur.execute("CREATE SCHEMA public;")
        conn.close()
        logger.info("Base de datos reseteada correctamente.")
    except Exception:
        logger.warning("No se pudo limpiar la base de datos.")


def analizar_escenario_con_dast(
    elemento: str, ruta_escenario: str, ruta_reporte: str, env: dict
) -> None:
    """
    Gestiona el ciclo de vida del servidor web temporal y ejecuta el análisis
    dinámico de SQLMap sobre el escenario específico.
    """

    resetear_base_de_datos()
    servidor_proceso = None

    # Inicialización del servidor web temporal.
    try:
        servidor_proceso = subprocess.Popen(
            [sys.executable, CODIGO_IA_FILENAME],
            cwd=ruta_escenario,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(TIEMPO_ESPERA_SERVIDOR)

    except Exception:
        logger.error(f"No se pudo iniciar el servidor en el escenario '{elemento}'.")
        return

    # Configuración del comando de SQLMap
    comando = (
        f"sqlmap -u {TARGET_URL} --batch --crawl=2 --forms "
        f"--dbms=postgresql --flush-session --level=5 --risk=3 "
        f'--technique=BETU --results-file="{ruta_reporte}"'
    )

    # Lanzamiento del escaneo dinámico y posterior limpieza del proceso.
    try:
        subprocess.run(
            comando,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
            env=env,
        )

    except Exception:
        logger.error(f"El escaneo no se procesó en el escenario '{elemento}'.")

    finally:
        if servidor_proceso:
            servidor_proceso.terminate()
            servidor_proceso.wait()


def ejecutar_dast_completo() -> None:
    """
    Función principal que valida el entorno del dataset, recorre secuencialmente
    los escenarios y coordina la fase de análisis dinámico.
    """
    logger.info("Fase 3: análisis dinámico.")

    if not os.path.exists(config.DATASET_DIR):
        logger.error(f"La carpeta de dataset no existe en {config.DATASET_DIR}.")
        return

    os.makedirs(config.DAST_REPORTS_DIR, exist_ok=True)

    env_utf8 = os.environ.copy()
    env_utf8["PYTHONUTF8"] = "1"

    # Escaneo secuencial del dataset.
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

        ruta_reporte = os.path.join(config.DAST_REPORTS_DIR, f"{elemento}_dast.csv")

        logger.info(f"Procesando {elemento}...")

        analizar_escenario_con_dast(elemento, ruta_escenario, ruta_reporte, env_utf8)


if __name__ == "__main__":
    ejecutar_dast_completo()
