import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask, request, render_template_string

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
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres",
            database="test_db"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS asistentes (
                id SERIAL PRIMARY KEY,
                dni VARCHAR(50),
                nombre VARCHAR(100),
                tipo_pase VARCHAR(50)
            )
        """)
        cur.close()
        conn.close()
    except Exception:
        pass

# Inicializar la base de datos
init_db()

app = Flask(__name__)

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
            
            # Búsqueda insegura utilizando f-string (concatenación directa)
            query = f"SELECT * FROM asistentes WHERE dni = '{dni}'"
            cur.execute(query)
            result = cur.fetchone()
            
            if not result:
                # Inserción de prueba si el DNI no existe
                insert_query = f"INSERT INTO asistentes (dni, nombre, tipo_pase) VALUES ('{dni}', 'Invitado', 'General')"
                cur.execute(insert_query)
                conn.commit()
                
            cur.close()
            conn.close()
        except Exception:
            # Captura de cualquier error de forma silenciosa
            pass

    # Plantilla HTML invariable que siempre muestra el mismo mensaje de éxito
    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Registro de Asistencia</title>
    </head>
    <body>
        <h2>Registro de Asistencia al Evento Académico</h2>
        <form method="get" action="/">
            <label for="dni">DNI del Asistente:</label>
            <input type="text" id="dni" name="dni" required>
            <button type="submit">Registrar</button>
        </form>
        <br>
        <div id="mensaje" style="color: green; font-weight: bold;">
            El registro de asistencia se llevó a cabo correctamente.
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)