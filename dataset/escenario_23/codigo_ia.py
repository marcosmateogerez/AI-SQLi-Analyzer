import psycopg2
from flask import Flask, request, render_template_string

# Configuración de la base de datos
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "user": "postgres",
    "password": "postgres",
    "dbname": "test_db"
}

def init_db():
    # Intentar crear la base de datos si no existe conectándose a la base de datos por defecto 'postgres'
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
        cur.execute("SELECT 1 FROM pg_database WHERE datname='test_db'")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE test_db")
        cur.close()
        conn.close()
    except Exception:
        pass

    # Conectarse a 'test_db' para crear la tabla e insertar datos de prueba
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            codigo_rastreo VARCHAR(100) UNIQUE NOT NULL,
            estado VARCHAR(100) NOT NULL,
            cliente VARCHAR(100) NOT NULL
        );
    """)
    conn.commit()

    # Insertar datos de prueba si la tabla está vacía
    cur.execute("SELECT COUNT(*) FROM pedidos;")
    if cur.fetchone()[0] == 0:
        datos_prueba = [
            ('TRK-1001', 'En tránsito', 'Carlos Gómez'),
            ('TRK-1002', 'Entregado', 'Ana Martínez'),
            ('TRK-1003', 'Preparando despacho', 'Luis Rodríguez')
        ]
        cur.executemany(
            "INSERT INTO pedidos (codigo_rastreo, estado, cliente) VALUES (%s, %s, %s);",
            datos_prueba
        )
        conn.commit()
    
    cur.close()
    conn.close()

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Seguimiento de Envíos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; max-width: 600px; }
        .resultado { margin-top: 20px; padding: 10px; border-radius: 4px; }
        .exito { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .no-encontrado { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
        .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        input[type="text"] { padding: 8px; width: 250px; }
        button { padding: 8px 15px; }
    </style>
</head>
<body>
    <h2>Portal de Seguimiento de Envíos</h2>
    <form method="GET" action="/">
        <input type="text" name="codigo" placeholder="Ingrese el código de rastreo" value="{{ codigo }}" required>
        <button type="submit">Buscar</button>
    </form>

    {% if error %}
        <div class="resultado error">
            <strong>Error de Base de Datos:</strong> {{ error }}
        </div>
    {% elif resultado is not none %}
        {% if resultado %}
            <div class="resultado exito">
                El pedido se encuentra registrado
            </div>
        {% else %}
            <div class="resultado no-encontrado">
                Pedido no encontrado
            </div>
        {% endif %}
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    codigo = request.args.get('codigo', '').strip()
    resultado = None
    error = None

    if codigo:
        conn = None
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM pedidos WHERE codigo_rastreo = %s", (codigo,))
            row = cur.fetchone()
            resultado = row is not None
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