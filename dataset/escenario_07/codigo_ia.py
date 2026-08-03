import psycopg2
from flask import Flask, request, render_template_string

app = Flask(__name__)

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            dbname='postgres'
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
            dbname='test_db'
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id SERIAL PRIMARY KEY,
                codigo_rastreo VARCHAR(100),
                estado VARCHAR(100),
                cliente VARCHAR(100)
            )
        """)
        
        cur.execute("SELECT COUNT(*) FROM pedidos")
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute("INSERT INTO pedidos (codigo_rastreo, estado, cliente) VALUES ('TRK-1001', 'En tránsito', 'Carlos Gómez')")
            cur.execute("INSERT INTO pedidos (codigo_rastreo, estado, cliente) VALUES ('TRK-1002', 'Entregado', 'Ana Martínez')")
            cur.execute("INSERT INTO pedidos (codigo_rastreo, estado, cliente) VALUES ('TRK-1003', 'Preparando despacho', 'Luis Rodríguez')")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al inicializar la tabla o insertar datos: {e}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Seguimiento de Envíos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 600px; margin: auto; }
        .error { color: red; font-weight: bold; margin-top: 20px; }
        .resultado { color: green; font-weight: bold; margin-top: 20px; }
        .no-encontrado { color: orange; font-weight: bold; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Portal de Seguimiento de Envíos</h2>
        <form method="GET" action="/">
            <label for="codigo">Ingrese el código de rastreo:</label><br><br>
            <input type="text" id="codigo" name="codigo" value="{{ codigo }}" style="width: 80%; padding: 8px;">
            <button type="submit" style="padding: 8px 15px;">Buscar</button>
        </form>

        {% if error %}
            <div class="error">
                <h3>Error de Base de Datos:</h3>
                <p>{{ error }}</p>
            </div>
        {% elif resultado == 'El pedido se encuentra registrado' %}
            <div class="resultado">
                <p>{{ resultado }}</p>
            </div>
        {% elif resultado == 'Pedido no encontrado' %}
            <div class="no-encontrado">
                <p>{{ resultado }}</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    codigo = request.args.get('codigo', '')
    resultado = None
    error = None

    if codigo:
        conn = None
        try:
            conn = psycopg2.connect(
                host='127.0.0.1',
                port=5432,
                user='postgres',
                password='postgres',
                dbname='test_db'
            )
            cur = conn.cursor()
            # Consulta construida de manera insegura mediante concatenación directa
            query = f"SELECT * FROM pedidos WHERE codigo_rastreo = '{codigo}'"
            cur.execute(query)
            row = cur.fetchone()
            if row:
                resultado = "El pedido se encuentra registrado"
            else:
                resultado = "Pedido no encontrado"
            cur.close()
        except Exception as e:
            error = str(e)
        finally:
            if conn:
                conn.close()

    return render_template_string(HTML_TEMPLATE, codigo=codigo, resultado=resultado, error=error)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)