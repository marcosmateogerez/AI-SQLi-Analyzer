import subprocess
import logging
import sys
import os

# Importación de la configuración.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Instanciación de logger para este módulo específico.
logger = logging.getLogger(__name__)

def ejecutar_sast_completo():
    """
    Ejecuta la fase completa de análisis estático utilizando Semgrep, donde
    recorre cada escenario de la carpeta /dataset, ejecuta Semgrep y guarda
    los reportes en results/sast_reports.
    """
    logger.info("Iniciando fase 2: análisis estático...")
    
    # Validación de que la carpeta de reportes exista antes de guardar.
    os.makedirs(config.SAST_REPORTS_DIR, exist_ok=True)
    if not os.path.exists(config.DATASET_DIR):
        logger.error(f"La carpeta de dataset no existe en {config.DATASET_DIR}.")
        return

    # Forzar entorno UTF-8 para el proceso interno.
    env_utf8 = os.environ.copy()
    env_utf8["PYTHONUTF8"] = "1"

    # Recorrido de los escenarios dentro de la carpeta /dataset.
    for elemento in os.listdir(config.DATASET_DIR):
        ruta_escenario = os.path.join(config.DATASET_DIR, elemento)

        if os.path.isdir(ruta_escenario):
            ruta_codigo = os.path.join(ruta_escenario, "codigo_ia.py")
            if not os.path.exists(ruta_codigo):
                logger.warning(f"Saltando {elemento}: no se encontró codigo_ia.py")
                continue
            
            ruta_reporte = os.path.join(config.SAST_REPORTS_DIR, f"{elemento}_sast.json")
            comando = [
                "semgrep",
                "--config=p/sql-injection",
                "--json",
                "-o", ruta_reporte,
                ruta_codigo
            ]

            # Ejecución del comando de Semgrep y captura de la salida.
            try:
                resultado = subprocess.run(
                    comando, 
                    capture_output=True, 
                    encoding="utf-8",
                    shell=True,
                    env=env_utf8
                )
                
                if os.path.exists(ruta_reporte):
                    logger.info(f"Reporte guardado correctamente en /results/sast_reports/{elemento}_sast.json")
                else:
                    logger.error(f"No se pudo generar el archivo de reporte: {resultado.stderr}.")

            except Exception as e:
                logger.error(f"Error al ejecutar Semgrep en {elemento}: {e}")

if __name__ == "__main__":
    ejecutar_sast_completo()