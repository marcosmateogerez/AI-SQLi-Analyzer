from inference.runner_inference import ejecutar_inferencia_completa
from sast.runner_sast import ejecutar_sast_completo
import logging
import sys
import os

# Configuración básica del logging para seguimiento de la ejecución.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Definición del directorio base de trabajo.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

def main():
    """
    Función principal que ejecuta el pipeline completo, el cual genera
    el código a partir de los escenarios, lo analiza con las herramientas
    de SAST y DAST, y finalmente genera un informe con los resultados obtenidos.
    """
    logger.info("Comienzo de ejecución del pipeline.")
    
    # Fase 1: inferencia.
    try:
        ejecutar_inferencia_completa()
    except Exception as e:
        logger.error(f"Error en la fase 1 de inferencia: {e}")
        sys.exit(1)
        
    logger.info("-" * 66)
    
    # Fase 2: SAST.
    try:
        ejecutar_sast_completo()
    except Exception as e:
        logger.error(f"Error en la fase 2 de SAST: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()