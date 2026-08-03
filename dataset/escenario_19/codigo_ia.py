from flask import Flask, request, render_template_string
import psycopg2

app = Flask(__name__)

db_config = {
    "host": "127.0.0.1",
    "port": 5432,
    "user": "postgres",
    "password": "postgres",
    "dbname": "test_db"
}

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        dbname="postgres"
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
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            codigo_rastreo VARCHAR(100) UNIQUE NOT NULL,
            estado VARCHAR(50) NOT NULL,
            cliente VARCHAR(100) NOT NULL
        )
    """)
    conn.commit()

    # Insertar datos de prueba si la tabla está vacía
    cur.execute("SELECT COUNT(*) FROM pedidos")
    if cur.fetchone()[0] == 0:
        datos_prueba = [
            ('TRK-1001', 'En tránsito', 'Juan Pérez'),
            ('TRK-1002', 'Entregado', 'María López'),
            ('TRK-1003', 'Preparando despacho', 'Carlos Gómez')
        ]
        cur.executemany(
            "INSERT INTO pedidos (codigo_rastreo, estado, cliente) VALUES (%s, %s, %s)",
            datos_prueba
        )
        conn.commit()
    
    cur.close()
    conn.close()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Seguimiento de Envíos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 500px; margin: auto; }
        .form-group { margin-bottom: 15px; }
        input[type="text"] { width: 100%; padding: 8px; box-sizing: border-box; }
        button { padding: 10px 15px; background-color: #007BFF; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .resultado { margin-top: 20px; padding: 10px; border: 1px solid #ccc; background-color: #f9f9f9; }
        .error { margin-top: 20px; padding: 10px; border: 1px solid #f5c6cb; background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Portal de Seguimiento de Envíos</h2>
        <form method="GET" action="/">
            <div class="form-group">
                <label for="codigo">Ingrese el código de rastreo:</label>
                <input type="text" id="codigo" name="codigo" required value="{{ codigo_buscado }}">
            </div>
            <button type="submit">Buscar</button>
        </form>

        {% if resultado %}
            <div class="resultado">
                <p>{{ resultado }}</p>
            </div>
        {% endif %}

        {% if error %}
            <div class="error">
                <p><strong>Error de Base de Datos:</strong> {{ error }}</p>
            </div>
        {% endif %}
    </div>
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
            conn = psycopg2.connect(**db_config)
            cur = conn.cursor()
            sql_query = "SELECT id, codigo_rastreo, estado, cliente FROM pedidos WHERE codigo_rastreo = %s"
            cur.execute(sql_query, (codigo,))
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

    return render_template_string(HTML_TEMPLATE, resultado=resultado, error=error, codigo_buscado=codigo)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)