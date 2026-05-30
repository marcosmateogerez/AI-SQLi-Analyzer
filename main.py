from inference.runner_inference import ejecutar_inferencia_completa
from sast.runner_sast import ejecutar_sast_completo
from dast.runner_dast import ejecutar_dast_completo
import logging
import config
import sys
import os

# Configuración básica del logging para seguimiento de la ejecución.
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    datefmt=config.LOG_DATE_FMT
)
logging.root.handlers[0].addFilter(lambda r: r.name.startswith("app"))
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
    # Fase 1: inferencia.
    try:
        ejecutar_inferencia_completa()
    except Exception as e:
        sys.exit(1)
    
    # Fase 2: SAST.
    try:
        ejecutar_sast_completo()
    except Exception as e:
        sys.exit(1)

    # Fase 3: DAST.
    try:
        ejecutar_dast_completo()
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    main()