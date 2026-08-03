import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask, request, render_template_string

DB_PARAMS = {
    "host": "127.0.0.1",
    "port": 5432,
    "user": "postgres",
    "password": "postgres"
}

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db'
    conn = psycopg2.connect(dbname="postgres", **DB_PARAMS)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    try:
        cur.execute("CREATE DATABASE test_db")
    except Exception:
        # Si ya existe, ignorar el error
        pass
    finally:
        cur.close()
        conn.close()

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    conn = psycopg2.connect(dbname="test_db", **DB_PARAMS)
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS asistentes (
                id SERIAL PRIMARY KEY,
                dni VARCHAR(50),
                nombre VARCHAR(100),
                tipo_pase VARCHAR(50)
            )
        """)
        conn.commit()

        # Insertar datos de prueba si la tabla está vacía
        cur.execute("SELECT COUNT(*) FROM asistentes")
        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO asistentes (dni, nombre, tipo_pase) VALUES
                ('12345678A', 'Juan Pérez', 'VIP'),
                ('87654321B', 'María López', 'General'),
                ('55555555C', 'Carlos Gómez', 'Expositor')
            """)
            conn.commit()
    except Exception:
        pass
    finally:
        cur.close()
        conn.close()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    dni = request.args.get('dni')
    
    if dni:
        try:
            conn = psycopg2.connect(dbname="test_db", **DB_PARAMS)
            cur = conn.cursor()
            sql_query = f"SELECT id, dni, nombre, tipo_pase FROM asistentes WHERE dni = '{dni}'"
            cur.execute(sql_query)
            cur.fetchall()
            cur.close()
            conn.close()
        except Exception:
            # Captura silenciosa de cualquier excepción
            pass

    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Verificación de Acreditaciones</title>
    </head>
    <body>
        <h2>Verificación de Acreditaciones</h2>
        <form method="GET" action="/">
            <label for="dni">DNI del Asistente:</label>
            <input type="text" id="dni" name="dni" required>
            <button type="submit">Verificar</button>
        </form>
        <p>Solicitud de verificación registrada en la auditoría</p>
    </body>
    </html>
    """
    return render_template_string(html_template)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)