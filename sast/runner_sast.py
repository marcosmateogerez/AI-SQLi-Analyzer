import subprocess
import logging
import config
import sys
import os

# Instanciación de logger para este módulo específico.
logger = logging.getLogger(f"app.{__name__}")

def ejecutar_sast_completo():
    """
    Ejecuta la fase completa de análisis estático utilizando Bandit, donde
    recorre cada escenario de la carpeta /dataset, ejecuta Bandit y guarda
    los reportes en results/sast_reports.
    """
    logger.info("Fase 2: análisis estático...")
    
    # Validación de que la carpeta de reportes exista antes de guardar.
    os.makedirs(config.SAST_REPORTS_DIR, exist_ok=True)
    if not os.path.exists(config.DATASET_DIR):
        logger.error(f"La carpeta de dataset no existe en {config.DATASET_DIR}.")
        return

    # Forzar entorno UTF-8 para evitar problemas de encoding en el subproceso.
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
            
            # Rutas para el almacenamiento de resultados.
            ruta_reporte = os.path.join(config.SAST_REPORTS_DIR, f"{elemento}_sast.json")
            comando = [
                sys.executable, "-m", "bandit",
                "--tests", "B608",
                "-f", "json",
                "-o", ruta_reporte,
                ruta_codigo
            ]

            # Ejecución del proceso de Bandit y captura de la salida.
            try:
                resultado = subprocess.run(
                    comando, 
                    capture_output=True, 
                    encoding="utf-8",
                    env=env_utf8
                )
                
                if resultado.returncode == 2:
                    logger.error(f"Bandit falló en {elemento}: {resultado.stderr}")
                elif not os.path.exists(ruta_reporte):
                    logger.error(f"No se generó el reporte para {elemento}: {resultado.stderr}")

            except Exception as e:
                logger.error(f"Error al ejecutar Bandit en {elemento}: {e}")

if __name__ == "__main__":
    ejecutar_sast_completo()