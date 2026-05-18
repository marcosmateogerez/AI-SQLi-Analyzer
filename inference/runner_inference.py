import os
import sys
import re
from google import genai
from google.genai import types

# Inyección de la raíz del proyecto en el path del sistema para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def limpiar_codigo_markdown(texto_crudo):
    """
    Los LLM suelen envolver el código en bloques ```python ... ```
    Esta función extrae únicamente el contenido de código ejecutable.
    """
    patron = r"```python\s*(.*?)\s*```"
    resultado = re.search(patron, texto_crudo, re.DOTALL)
    if resultado:
        return resultado.group(1).strip()
    return texto_crudo.strip()

def ejecutar_inferencia_completa():
    print("[*] Iniciando Fase 1: Inferencia con la nueva Gemini API...")
    print(f"[*] Utilizando el modelo: {config.LLM_MODEL}")
    
    # Validación estricta del archivo .env
    if not config.GEMINI_API_KEY:
        print("[!] ERROR CRÍTICO: No se detectó la variable GEMINI_API_KEY.")
        print("    Asegurate de haber creado el archivo .env en la raíz y configurado la clave.")
        return

    # Inicializar el nuevo cliente oficial de Gemini
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    # Configuración de replicabilidad científica usando la nueva SDK
    config_generacion = types.GenerateContentConfig(
        temperature=0.0,
        seed=42
    )

    if not os.path.exists(config.DATASET_DIR):
        print(f"[!] Error: La carpeta de dataset no existe en {config.DATASET_DIR}")
        return

    # Escaneo secuencial de los casos de uso en el dataset
    for elemento in os.listdir(config.DATASET_DIR):
        ruta_escenario = os.path.join(config.DATASET_DIR, elemento)
        
        if os.path.isdir(ruta_escenario):
            ruta_prompt = os.path.join(ruta_escenario, "prompt.txt")
            ruta_salida_codigo = os.path.join(ruta_escenario, "codigo_ia.py")

            if not os.path.exists(ruta_prompt):
                continue

            print(f"[+] Consultando API para: {elemento}... (Temp: 0.0, Seed: 42)")

            with open(ruta_prompt, "r", encoding="utf-8") as f:
                prompt_contenido = f.read()

            try:
                # Nueva sintaxis para generar contenido con el cliente unificado
                respuesta = client.models.generate_content(
                    model=config.LLM_MODEL,
                    contents=prompt_contenido,
                    config=config_generacion
                )
                texto_respuesta = respuesta.text

                # Parseo del bloque Markdown
                codigo_limpio = limpiar_codigo_markdown(texto_respuesta)

                # Escritura física del archivo de código de la IA
                with open(ruta_salida_codigo, "w", encoding="utf-8") as f:
                    f.write(codigo_limpio)
                
                print(f"    [✔] Código generado con éxito en {elemento}/codigo_ia.py")

            except Exception as e:
                print(f"    [!] Error al procesar {elemento}: {e}")

if __name__ == "__main__":
    ejecutar_inferencia_completa()