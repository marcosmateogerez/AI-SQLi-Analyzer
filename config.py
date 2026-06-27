from dotenv import load_dotenv
import os

# Configuración de logging.
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"

# Rutas absolutas.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
SAST_REPORTS_DIR = os.path.join(RESULTS_DIR, "sast_reports")
DAST_REPORTS_DIR = os.path.join(RESULTS_DIR, "dast_reports")

# Carga el archivo .env desde la raíz del proyecto.
ruta_env = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ruta_env)

# Configuración del LLM.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_MODEL = "gemini-2.5-flash"