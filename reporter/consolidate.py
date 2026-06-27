import logging
import config
import json
import csv
import os
import re

# Instanciación de logger para este módulo específico.
logger = logging.getLogger(f"app.{__name__}")

def extraer_id_escenario(filename):
    """
    Extrae el identificador del escenario a partir del nombre del archivo.
    Ejemplo: 'escenario_01_sast.json' -> 'escenario_01'
    """
    match = re.match(r'(escenario_\d+)', filename)
    return match.group(1) if match else None

def procesar_sast(path):
    """Determina si Bandit encontró vulnerabilidades."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for hallazgo in data.get("results", []):
            if hallazgo.get("test_id") == "B608":
                return True
                
        return False
    except Exception:
        return False

def procesar_dast(path):
    """Determina si SQLMap logró explotar la vulnerabilidad."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            lineas = [linea for linea in f if linea.strip()]
            return len(lineas) > 1
    except Exception:
        return False

def generar_resumen_completo():
    """Escanea los directorios de configuración y genera el CSV maestro."""
    logger.info("Fase 4: generación de resumen con los resultados...")
    sast_dir = config.SAST_REPORTS_DIR
    dast_dir = config.DAST_REPORTS_DIR
    output_csv = os.path.join(config.RESULTS_DIR, "resumen_resultados.csv")

    escenarios = set()
    if os.path.exists(sast_dir):
        for f in os.listdir(sast_dir):
            escenario_id = extraer_id_escenario(f)
            if escenario_id: escenarios.add(escenario_id)
            
    if os.path.exists(dast_dir):
        for f in os.listdir(dast_dir):
            escenario_id = extraer_id_escenario(f)
            if escenario_id: escenarios.add(escenario_id)

    if not escenarios:
        return

    escenarios_ordenados = sorted(list(escenarios))
    filas_resumen = []

    for esc_id in escenarios_ordenados:
        sast_path = os.path.join(sast_dir, f"{esc_id}_sast.json")
        dast_path = os.path.join(dast_dir, f"{esc_id}_dast.csv")

        hubo_sast = procesar_sast(sast_path)
        hubo_dast = procesar_dast(dast_path)

        filas_resumen.append([esc_id, hubo_sast, hubo_dast])

    try:
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Escenario", "SAST", "DAST"])
            writer.writerows(filas_resumen)
    except Exception as e:
        logger.error(f"No se pudo escribir en el archivo resumen: {e}")