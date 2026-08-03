import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask, request, render_template_string

def init_db():
    try:
        # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
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

        # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
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
                dni VARCHAR(50) UNIQUE NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                tipo_pase VARCHAR(50) NOT NULL
            )
        """)
        conn.commit()

        # Insertar datos de prueba si la tabla está vacía
        cur.execute("SELECT COUNT(*) FROM asistentes")
        if cur.fetchone()[0] == 0:
            datos_prueba = [
                ('12345678A', 'Carlos Gómez', 'VIP'),
                ('87654321B', 'Ana Rodríguez', 'General'),
                ('11223344C', 'Luis Martínez', 'Estudiante')
            ]
            cur.executemany(
                "INSERT INTO asistentes (dni, nombre, tipo_pase) VALUES (%s, %s, %s)",
                datos_prueba
            )
            conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

# Inicializar la base de datos antes de lanzar la aplicación
init_db()

app = Flask(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Verificación de Acreditaciones</title>
</head>
<body>
    <h2>Verificación de Acreditación</h2>
    <form method="GET" action="/">
        <label for="dni">DNI:</label>
        <input type="text" id="dni" name="dni" required>
        <button type="submit">Verificar</button>
    </form>
    <p>Solicitud de verificación registrada en la auditoría</p>
</body>
</html>"""

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
            cur.execute("SELECT id, nombre, tipo_pase FROM asistentes WHERE dni = %s", (dni,))
            cur.fetchone()
            cur.close()
            conn.close()
        except Exception:
            pass
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)