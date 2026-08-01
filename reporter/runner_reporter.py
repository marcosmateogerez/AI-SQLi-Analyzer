import csv
import logging
import os
import re

import config

# Configuración de Logging.
logger = logging.getLogger(f"app.{__name__}")

# Constantes globales del módulo.
CSV_HEADER = ["Escenario", "SAST", "DAST", "Tipos de SQLi encontrados"]
RESUMEN_FILENAME = "resumen_resultados.csv"

# Mapeo de códigos de SQLMap a nombres completos.
MAPA_TECNICAS_SQLMAP = {
    "B": "boolean-based",
    "E": "error-based",
    "T": "time-based",
    "U": "union-based",
}


def extraer_id_escenario(filename: str) -> str | None:
    """
    Extrae el identificador del escenario a partir del nombre del archivo.
    """
    match = re.match(r"(escenario_\d+)", filename)
    return match.group(1) if match else None


def procesar_sast(path: str) -> bool:
    """
    Determina si Bandit encontró vulnerabilidades de SQL Injection
    analizando el reporte estructurado en formato JSON.
    """
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            import json

            data = json.load(f)

        for hallazgo in data.get("results", []):
            if hallazgo.get("test_id") == "B608":
                return True

        return False
    except Exception:
        return False


def procesar_dast(path: str) -> tuple[bool, str]:
    """
    Determina si SQLMap encontró vulnerabilidades analizando
    el reporte en formato CSV.
    """
    if not os.path.exists(path):
        return False, "-"
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            tecnicas_encontradas = set()

            for row in reader:
                tech_raw = row.get("Technique(s)", "").strip()
                for char in tech_raw.upper():
                    if char in MAPA_TECNICAS_SQLMAP:
                        tecnicas_encontradas.add(MAPA_TECNICAS_SQLMAP[char])

            if tecnicas_encontradas:
                cadena_tecnicas = ", ".join(sorted(tecnicas_encontradas))
                return True, cadena_tecnicas

        return False, "-"
    except Exception:
        return False, "Error"


def recolectar_ids_escenarios(sast_dir: str, dast_dir: str) -> list[str]:
    """
    Escanea las carpetas de reportes SAST y DAST para consolidar y ordenar
    un conjunto único de identificadores de escenarios procesados.
    """
    escenarios = set()

    if os.path.exists(sast_dir):
        for f in os.listdir(sast_dir):
            escenario_id = extraer_id_escenario(f)
            if escenario_id:
                escenarios.add(escenario_id)

    if os.path.exists(dast_dir):
        for f in os.listdir(dast_dir):
            escenario_id = extraer_id_escenario(f)
            if escenario_id:
                escenarios.add(escenario_id)

    return sorted(escenarios)


def escribir_csv_resumen(ruta_csv: str, filas: list[list]) -> None:
    """
    Maneja la apertura física del archivo de resultados e inyecta las
    filas procesadas con el formato CSV.
    """
    try:
        with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(CSV_HEADER)
            writer.writerows(filas)
    except Exception:
        logger.error(
            "Error al escribir el archivo de resumen, no se pudo guardar el reporte."
        )


def generar_resumen_completo() -> None:
    """
    Función principal que escanea las carpetas de reportes, y genera
    el resumen con los resultados en un archivo CSV.
    """
    logger.info("Fase 4: generación de resumen con los resultados.")

    sast_dir = config.SAST_REPORTS_DIR
    grid_dir = config.DAST_REPORTS_DIR
    output_csv = os.path.join(config.RESULTS_DIR, RESUMEN_FILENAME)

    escenarios_ordenados = recolectar_ids_escenarios(sast_dir, grid_dir)

    if not escenarios_ordenados:
        logger.warning(
            "No se encontraron reportes previos para consolidar en el resumen."
        )
        return

    # Asegura que la carpeta destino de los resultados consolidados exista.
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    filas_resumen = []

    # Procesamiento individual de cada escenario.
    for esc_id in escenarios_ordenados:
        sast_path = os.path.join(sast_dir, f"{esc_id}_sast.json")
        dast_path = os.path.join(grid_dir, f"{esc_id}_dast.csv")

        hubo_sast = procesar_sast(sast_path)
        hubo_dast, tecnicas_dast = procesar_dast(dast_path)

        logger.info(f"Procesando {esc_id}...")

        filas_resumen.append([esc_id, hubo_sast, hubo_dast, tecnicas_dast])

    escribir_csv_resumen(output_csv, filas_resumen)


if __name__ == "__main__":
    generar_resumen_completo()
