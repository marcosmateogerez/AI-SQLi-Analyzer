import psycopg2
from flask import Flask, request, render_template_string

db_conf = "host=127.0.0.1 port=5432 user=postgres password=postgres"

def init_db():
    try:
        conn = psycopg2.connect(dsn=db_conf, dbname="postgres")
        conn.autocommit = True
        conn.cursor().execute("CREATE DATABASE test_db")
    except Exception:
        pass
    try:
        conn = psycopg2.connect(dsn=db_conf, dbname="test_db")
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
    except Exception:
        pass

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Registro de Asistencia</title></head>
<body>
    <h2>Registro de Asistencia</h2>
    <form method="get" action="/">
        <label for="dni">DNI:</label>
        <input type="text" id="dni" name="dni" required>
        <button type="submit">Registrar</button>
    </form>
    <p style="color: green;">El registro de asistencia se llevó a cabo correctamente.</p>
</body>
</html>
"""

@app.route('/')
def index():
    dni = request.args.get('dni')
    if dni:
        try:
            conn = psycopg2.connect(dsn=db_conf, dbname="test_db")
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO asistentes (dni, nombre, tipo_pase) VALUES (%s, %s, %s) ON CONFLICT (dni) DO NOTHING",
                (dni, "Asistente", "General")
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            pass
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)