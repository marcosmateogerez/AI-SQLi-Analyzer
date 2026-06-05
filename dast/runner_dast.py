import subprocess
import logging
import config
import time
import sys
import os

# Instanciación de logger para este módulo específico.
logger = logging.getLogger(f"app.{__name__}")

def ejecutar_dast_completo():
    """
    Ejecuta la fase completa de análisis dinámico utilizando SQLMap, donde
    recorre cada escenario de la carpeta /dataset, ejecuta SQLMap y guarda 
    los reportes en results/dast_reports.
    """
    logger.info("Fase 3: análisis dinámico...")
    
    # Validación de que la carpeta de reportes exista antes de guardar.
    os.makedirs(config.DAST_REPORTS_DIR, exist_ok=True)
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
            ruta_reporte = os.path.join(config.DAST_REPORTS_DIR, f"{elemento}_dast.csv")
            
            # URL local donde el servidor temporal de flask va a estar escuchando.
            target_url = "http://127.0.0.1:5000"
            
            # Ejecución del servidor temporal para el escenario actual.
            servidor_proceso = None
            try:
                servidor_proceso = subprocess.Popen(
                    [sys.executable, "codigo_ia.py"],
                    cwd=ruta_escenario,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"No se pudo inicializar el servidor para {elemento}: {e}")
                continue

            # Configuración de SQLMap para el análisis.
            comando = (
                f'sqlmap -u {target_url} --batch --crawl=2 --forms '
                f'--dbms=sqlite --flush-session --level=5 --risk=3 '
                f'--results-file="{ruta_reporte}"'
            )
            
            # Ejecución del proceso de SQLMap y captura de la salida.
            try:
                subprocess.run(
                    comando, 
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=True,
                    env=env_utf8
                )
            
            except Exception as e:
                logger.error(f"Error durante el escaneo de SQLMap en {elemento}: {e}")
                
            finally:
                if servidor_proceso:
                    servidor_proceso.terminate()
                    servidor_proceso.wait()

if __name__ == "__main__":
    ejecutar_dast_completo()