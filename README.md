```markdown
# AI-SQLi-Analyzer

Pipeline automatizado para la detección de SQL Injection en el código generado por inteligencia artificial.

---

## 📂 Estructura del proyecto

El proyecto se organiza de la siguiente manera:

* **inference/**: Carpeta que contiene los componentes para la generación del código fuente de los escenarios.
* **sast/**: Carpeta que contiene los componentes para realizar el análisis estático.
* **dast/**: Carpeta que contiene los componentes para realizar el análisis dinámico.
* **dataset/**: Almacena las carpetas independientes de cada escenario de código fuente generado.
* **results/**: Carpeta central de resultados. Está organizada internamente en dos subcarpetas (`sast_reports` y `dast_reports`), donde se guarda un único archivo de resultado por el procesamiento de cada código.

---

## 🛠️ Requisitos e instalación

Para instalar todas las herramientas y dependencias necesarias para el funcionamiento del proyecto, simplemente se debe ejecutar el archivo correspondiente:

```bash
py requirements.py
```

---

## ⚙️ Configuración del entorno

Se debe crear un archivo llamado `.env` en la raíz del proyecto que contenga la variable de entorno con la clave de acceso:

```env
GEMINI_API_KEY=tu_clave_de_google_aquí
```

---

## 🚀 Instrucciones de ejecución

Para iniciar todo el proceso, se debe ejecutar el script principal desde la terminal ubicada en la raíz del proyecto:

```bash
py main.py
```