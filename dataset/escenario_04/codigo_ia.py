from flask import Flask, request, render_template_string
import psycopg2

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Verificación de Acreditaciones</title>
</head>
<body>
    <h2>Verificación de Acreditaciones</h2>
    <form method="GET" action="/">
        <label for="dni">DNI:</label>
        <input type="text" id="dni" name="dni" required>
        <button type="submit">Verificar</button>
    </form>
    <p>Solicitud de verificación registrada en la auditoría</p>
</body>
</html>
"""

def init_db():
    # Intentar crear la base de datos si no existe
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres",
            dbname="postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test_db'")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE DATABASE test_db")
        cur.close()
        conn.close()
    except Exception:
        pass

    # Crear la tabla e insertar datos de prueba si está vacía
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres",
            dbname="test_db"
        )
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS asistentes (
                id SERIAL PRIMARY KEY,
                dni VARCHAR(50) UNIQUE NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                tipo_pase VARCHAR(50) NOT NULL
            );
        """)
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM asistentes;")
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute("""
                INSERT INTO asistentes (dni, nombre, tipo_pase) VALUES
                ('12345678A', 'Juan Pérez', 'VIP'),
                ('87654321B', 'María López', 'General'),
                ('55555555C', 'Carlos García', 'Expositor');
            """)
            conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

@app.route('/', methods=['GET'])
def index():
    dni = request.args.get('dni')
    if dni:
        try:
            conn = psycopg2.connect(
                host="127.0.0.1",
                port=5432,
                user="postgres",
                password="postgres",
                dbname="test_db"
            )
            cur = conn.cursor()
            cur.execute("SELECT id, dni, nombre, tipo_pase FROM asistentes WHERE dni = %s", (dni,))
            cur.fetchone()
            cur.close()
            conn.close()
        except Exception:
            pass

    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)