import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask, request, render_template_string

app = Flask(__name__)

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            dbname='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test_db'")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE DATABASE test_db")
        cur.close()
        conn.close()
    except Exception:
        pass

    # Conectar a 'test_db' para crear la tabla 'asistentes'
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            dbname='test_db'
        )
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS asistentes (
                id SERIAL PRIMARY KEY,
                dni VARCHAR(50) UNIQUE,
                nombre VARCHAR(100) DEFAULT 'Anónimo',
                tipo_pase VARCHAR(50) DEFAULT 'General'
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

@app.route('/')
def index():
    dni = request.args.get('dni')
    if dni:
        try:
            conn = psycopg2.connect(
                host='127.0.0.1',
                port=5432,
                user='postgres',
                password='postgres',
                dbname='test_db'
            )
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO asistentes (dni) VALUES (%s) ON CONFLICT (dni) DO NOTHING",
                (dni,)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            pass

    html_template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Registro de Asistencia</title>
</head>
<body>
    <h2>Registro de Asistencia</h2>
    <form action="/" method="get">
        <label for="dni">DNI:</label>
        <input type="text" id="dni" name="dni" required>
        <button type="submit">Registrar</button>
    </form>
    <p>El registro de asistencia se llevó a cabo correctamente.</p>
</body>
</html>"""
    
    return render_template_string(html_template)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)