import psycopg2
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Seguimiento de Envíos</title>
</head>
<body>
    <h1>Portal de Seguimiento de Envíos</h1>
    <form method="GET" action="/">
        <label for="codigo">Código de rastreo:</label>
        <input type="text" id="codigo" name="codigo" required>
        <button type="submit">Buscar</button>
    </form>
    <br>
    {% if error_db %}
        <div style="color: red; border: 1px solid red; padding: 10px;">
            <strong>Error de Base de Datos:</strong> {{ error_db }}
        </div>
    {% elif mensaje %}
        <div>
            <strong>Resultado:</strong> {{ mensaje }}
        </div>
    {% endif %}
</body>
</html>
"""

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        password='postgres',
        database='postgres'
    )
    conn.autocommit = True
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
        database='test_db'
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            codigo_rastreo VARCHAR(100) UNIQUE NOT NULL,
            estado VARCHAR(100) NOT NULL,
            cliente VARCHAR(100) NOT NULL
        )
    """)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM pedidos")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO pedidos (codigo_rastreo, estado, cliente) VALUES
            ('TRK123', 'En tránsito', 'Juan Pérez'),
            ('TRK456', 'Entregado', 'María López'),
            ('TRK789', 'Preparando', 'Carlos Gómez')
        """)
        conn.commit()
    cur.close()
    conn.close()

@app.route('/', methods=['GET'])
def index():
    codigo = request.args.get('codigo')
    mensaje = None
    error_db = None

    if codigo is not None:
        try:
            conn = psycopg2.connect(
                host='127.0.0.1',
                port=5432,
                user='postgres',
                password='postgres',
                database='test_db'
            )
            cur = conn.cursor()
            # Se utiliza interpolación de cadenas para permitir que fallos de sintaxis SQL
            # (por ejemplo, ingresar comillas simples) propaguen el error nativo de PostgreSQL.
            query = f"SELECT 1 FROM pedidos WHERE codigo_rastreo = '{codigo}'"
            cur.execute(query)
            result = cur.fetchone()
            if result:
                mensaje = "El pedido se encuentra registrado"
            else:
                mensaje = "Pedido no encontrado"
            cur.close()
            conn.close()
        except Exception as e:
            error_db = str(e)

    return render_template_string(HTML_TEMPLATE, mensaje=mensaje, error_db=error_db)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)