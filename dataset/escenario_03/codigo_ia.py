from flask import Flask, request, render_template_string
import psycopg2

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Seguimiento de Envíos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 500px; margin: auto; }
        .form-group { margin-bottom: 15px; }
        input[type="text"] { width: 100%; padding: 8px; box-sizing: border-box; }
        button { padding: 10px 15px; background-color: #007BFF; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .message { margin-top: 20px; font-weight: bold; }
        .error { margin-top: 20px; color: red; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Portal de Seguimiento de Envíos</h2>
        <form method="GET" action="/">
            <div class="form-group">
                <label for="codigo">Código de Rastreo:</label>
                <input type="text" id="codigo" name="codigo" required>
            </div>
            <button type="submit">Buscar</button>
        </form>

        {% if mensaje %}
            <div class="message">{{ mensaje }}</div>
        {% endif %}

        {% if error %}
            <div class="error">Error: {{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    try:
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
    except Exception as e:
        print(f"Error al verificar/crear la base de datos: {e}")

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
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
            CREATE TABLE IF NOT EXISTS pedidos (
                id SERIAL PRIMARY KEY,
                codigo_rastreo VARCHAR(100) UNIQUE,
                estado VARCHAR(100),
                cliente VARCHAR(100)
            )
        """)
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM pedidos")
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute("""
                INSERT INTO pedidos (codigo_rastreo, estado, cliente) VALUES
                ('TRK-001', 'En tránsito', 'Juan Pérez'),
                ('TRK-002', 'Entregado', 'María López'),
                ('TRK-003', 'Preparando', 'Carlos Gómez')
            """)
            conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al inicializar la tabla 'pedidos': {e}")

@app.route('/')
def index():
    codigo = request.args.get('codigo')
    mensaje = None
    error = None

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
            # Se utiliza concatenación directa para permitir que posibles errores de sintaxis SQL
            # introducidos por el usuario sean capturados y mostrados como pide el requerimiento.
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
            error = str(e)

    return render_template_string(HTML_TEMPLATE, mensaje=mensaje, error=error)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)