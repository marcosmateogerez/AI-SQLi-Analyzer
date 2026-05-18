import os
from dotenv import load_dotenv

# 1. Rutas Estructurales Absolutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
SAST_REPORTS_DIR = os.path.join(RESULTS_DIR, "sast_reports")

# Cargar el archivo .env de forma explícita desde la raíz del proyecto
ruta_env = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ruta_env)

# 2. Configuración del LLM (Leída estrictamente del entorno)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_MODEL = "gemini-3-flash-preview"  # Selección del modelo de última generación