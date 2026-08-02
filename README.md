# Pipeline para la detección de SQL Injection en el código generado por inteligencia artificial

---

## 📂 Estructura del proyecto

El proyecto se organiza de la siguiente manera:

* **inference/**: carpeta que contiene los componentes para la generación del código fuente de los escenarios.
* **sast/**: carpeta que contiene los componentes para realizar el análisis estático.
* **dast/**: carpeta que contiene los componentes para realizar el análisis dinámico.
* **reporter/**: carpeta que contiene los componentes para la consolidación de los reportes generados por SAST y DAST.
* **dataset/**: almacena las carpetas independientes de cada escenario de código fuente generado.
* **results/**: carpeta central de resultados. Está organizada internamente en dos subcarpetas (`sast_reports` y `dast_reports`) para los reportes individuales por código, y almacena el archivo final unificado (`resumen_resultados.csv`) con el estado de todos los escenarios.

---

## 🛠️ Requisitos e instalación

**Prerrequisitos**: tener instalado **Docker** y **Docker Compose** en el sistema.

---

## ⚙️ Configuración del entorno

Se debe crear un archivo llamado `.env` en la raíz del proyecto que contenga la variable de entorno con la clave de acceso:

```env
GEMINI_API_KEY=<CLAVE_API_DE_GOOGLE>
```

---

## 🚀 Instrucciones de ejecución

Para iniciar todo el proceso, se debe ejecutar el script principal desde la terminal ubicada en la raíz del proyecto:

```bash
docker compose up --build
```

### Detener el entorno

Para detener la ejecución de los servicios, corra en la terminal:

```bash
docker compose down