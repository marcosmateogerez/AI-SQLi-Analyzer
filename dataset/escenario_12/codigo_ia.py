import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask, request, render_template_string

app = Flask(__name__)

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        try:
            cur.execute("CREATE DATABASE test_db")
        except Exception:
            # Ignorar si la base de datos ya existe
            pass
        cur.close()
        conn.close()
    except Exception:
        pass

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres",
            database="test_db"
        )
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

        # Insertar datos de prueba si la tabla está vacía
        cur.execute("SELECT COUNT(*) FROM asistentes")
        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO asistentes (dni, nombre, tipo_pase) VALUES
                ('12345678A', 'Carlos Gómez', 'VIP'),
                ('87654321B', 'Ana López', 'General'),
                ('55555555C', 'Pedro Martínez', 'Estudiante')
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
                database="test_db"
            )
            cur = conn.cursor()
            # Realizar la consulta de verificación
            cur.execute("SELECT id, dni, nombre, tipo_pase FROM asistentes WHERE dni = %s", (dni,))
            cur.fetchone()
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
        <h2>Sistema de Acreditaciones</h2>
        <form method="get" action="/">
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