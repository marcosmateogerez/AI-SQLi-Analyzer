import os
import subprocess
import venv

# Constantes de configuración.
VENV_DIR = ".venv"

# Lista de dependencias del proyecto.
librerias = [
    "bandit==1.9.4",
    "flask==3.1.3",
    "google-genai==2.9.0",
    "python-dotenv==1.2.2",
    "sqlmap==1.10.7",
]

# Determinar el ejecutable de Python según el sistema operativo.
if os.name == "nt":
    python_virtual = os.path.join(VENV_DIR, "Scripts", "python.exe")
else:
    python_virtual = os.path.join(VENV_DIR, "bin", "python")


def main():
    # Si el entorno virtual no existe, lo crea.
    if not os.path.exists(VENV_DIR):
        venv.create(VENV_DIR, with_pip=True)

    # Actualizar pip en caso de que no esté actualizado.
    subprocess.run(
        [python_virtual, "-m", "pip", "install", "--upgrade", "pip"], check=True
    )

    # Instalar la lista de dependencias.
    subprocess.run([python_virtual, "-m", "pip", "install", *librerias], check=True)


if __name__ == "__main__":
    main()
