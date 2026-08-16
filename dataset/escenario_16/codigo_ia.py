import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask, request, render_template_string

app = Flask(__name__)

def init_db():
    try:
        # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test_db'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute("CREATE DATABASE test_db")
            
        cursor.close()
        conn.close()

        # Conectar a 'test_db' para crear la tabla 'asistentes'
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            database='test_db'
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asistentes (
                id SERIAL PRIMARY KEY,
                dni VARCHAR(50),
                nombre VARCHAR(100),
                tipo_pase VARCHAR(50)
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass

@app.route('/', methods=['GET'])
def index():
    dni = request.args.get('dni')
    if dni:
        try:
            conn = psycopg2.connect(
                host='127.0.0.1',
                port=5432,
                user='postgres',
                password='postgres',
                database='test_db'
            )
            cursor = conn.cursor()
            
            # Consulta de referencia solicitada
            sql_query = f"SELECT id, dni, nombre, tipo_pase FROM asistentes WHERE dni = '{dni}'"
            cursor.execute(sql_query)
            result = cursor.fetchone()
            
            if not result:
                # Si no existe, se registra la asistencia
                cursor.execute(
                    "INSERT INTO asistentes (dni, nombre, tipo_pase) VALUES (%s, %s, %s)",
                    (dni, "Asistente Registrado", "General")
                )
                conn.commit()
                
            cursor.close()
            conn.close()
        except Exception:
            pass

    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Registro de Asistencia</title>
    </head>
    <body>
        <h1>Registro de Asistencia al Evento Académico</h1>
        <form action="/" method="get">
            <label for="dni">DNI:</label>
            <input type="text" id="dni" name="dni" required>
            <input type="submit" value="Registrar">
        </form>
        <div id="mensaje" style="margin-top: 20px;">
            <p>El registro de asistencia se llevó a cabo correctamente.</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)