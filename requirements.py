import subprocess
import sys

# Lista de dependencias del proyecto.
librerias = [
    "google-genai",
    "python-dotenv==1.2.2",
    "bandit",
    "sqlmap",
    "flask"
]
subprocess.run([sys.executable, "-m", "pip", "install", *librerias])