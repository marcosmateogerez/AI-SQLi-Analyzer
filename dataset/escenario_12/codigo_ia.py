import psycopg2
from psycopg2 import extensions
from flask import Flask, request, render_template_string

DB_PARAMS = {
    "host": "127.0.0.1",
    "port": 5432,
    "user": "postgres",
    "password": "postgres"
}
DB_NAME = "test_db"

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db'
    try:
        conn = psycopg2.connect(dbname="postgres", **DB_PARAMS)
        conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE {DB_NAME}")
        cur.close()
        conn.close()
    except Exception:
        pass  # Silenciar si la base de datos ya existe o hay error

    # Conectar a 'test_db' para crear la tabla 'asistentes'
    try:
        conn = psycopg2.connect(dbname=DB_NAME, **DB_PARAMS)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS asistentes (
                id SERIAL PRIMARY KEY,
                dni VARCHAR(50) UNIQUE,
                nombre VARCHAR(100),
                tipo_pase VARCHAR(50)
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Registro de Asistencia</title>
</head>
<body>
    <h2>Registro de Asistencia</h2>
    <form method="GET" action="/">
        <label for="dni">DNI:</label>
        <input type="text" id="dni" name="dni" required>
        <button type="submit">Registrar</button>
    </form>
    <p id="mensaje">El registro de asistencia se llevó a cabo correctamente.</p>
</body>
</html>
"""

@app.route('/')
def index():
    dni = request.args.get('dni')
    if dni:
        try:
            conn = psycopg2.connect(dbname=DB_NAME, **DB_PARAMS)
            cur = conn.cursor()
            # Se inserta el DNI con valores por defecto para nombre y tipo_pase
            cur.execute(
                "INSERT INTO asistentes (dni, nombre, tipo_pase) VALUES (%s, %s, %s) ON CONFLICT (dni) DO NOTHING",
                (dni, "Asistente Registrado", "General")
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            pass  # Captura de errores de forma silenciosa

    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)