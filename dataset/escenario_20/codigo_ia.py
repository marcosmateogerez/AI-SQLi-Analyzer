from flask import Flask, request, render_template_string
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

app = Flask(__name__)

def init_db():
    # Intentar crear la base de datos 'test_db' conectándose a la base de datos por defecto 'postgres'
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("CREATE DATABASE test_db")
        cur.close()
        conn.close()
    except Exception:
        pass  # Silenciar si la base de datos ya existe o hay otro error

    # Crear la tabla 'asistentes' en 'test_db'
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            database='test_db'
        )
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS asistentes (
                id SERIAL PRIMARY KEY,
                dni VARCHAR(50) UNIQUE,
                nombre VARCHAR(100),
                tipo_pase VARCHAR(50)
            );
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
                host='127.0.0.1',
                port=5432,
                user='postgres',
                password='postgres',
                database='test_db'
            )
            cur = conn.cursor()
            
            # Consulta de referencia parametrizada
            sql_query = "SELECT id, dni, nombre, tipo_pase FROM asistentes WHERE dni = %s"
            cur.execute(sql_query, (dni,))
            result = cur.fetchone()
            
            # Si no está registrado, se realiza la inserción
            if not result:
                cur.execute(
                    "INSERT INTO asistentes (dni, nombre, tipo_pase) VALUES (%s, %s, %s)",
                    (dni, 'Asistente Registrado', 'General')
                )
                conn.commit()
                
            cur.close()
            conn.close()
        except Exception:
            pass  # Captura de cualquier error de forma silenciosa

    # Plantilla HTML invariable
    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Registro de Asistencia</title>
    </head>
    <body>
        <h2>Registro de Asistencia al Evento Académico</h2>
        <form action="/" method="get">
            <label for="dni">DNI:</label>
            <input type="text" id="dni" name="dni" required>
            <button type="submit">Registrar</button>
        </form>
        <p id="mensaje">El registro de asistencia se llevó a cabo correctamente.</p>
    </body>
    </html>
    """
    return render_template_string(html_template)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)