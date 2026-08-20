import psycopg2
from psycopg2 import errors
from flask import Flask, request, render_template_string

# Configuración de la base de datos
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'test_db'
}

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
    try:
        cur.execute("CREATE DATABASE test_db")
    except psycopg2.errors.DuplicateDatabase:
        pass
    finally:
        cur.close()
        conn.close()

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            codigo_rastreo VARCHAR(50) UNIQUE NOT NULL,
            estado VARCHAR(50) NOT NULL,
            cliente VARCHAR(100) NOT NULL
        )
    """)
    
    # Insertar datos de prueba si la tabla está vacía
    cur.execute("SELECT COUNT(*) FROM pedidos")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO pedidos (codigo_rastreo, estado, cliente) VALUES
            ('TRK123456', 'En tránsito', 'Juan Pérez'),
            ('TRK789012', 'Entregado', 'María López'),
            ('TRK345678', 'Procesando', 'Carlos Gómez')
        """)
        
    cur.close()
    conn.close()

app = Flask(__name__)

@app.route('/')
def index():
    codigo = request.args.get('codigo')
    resultado = None
    error = None
    
    if codigo is not None:
        conn = None
        try:
            conn = psycopg2.connect(**DB_CONFIG)
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

    template = """
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
            .result { margin-top: 20px; padding: 10px; border: 1px solid #ccc; background-color: #f9f9f9; }
            .error { margin-top: 20px; padding: 10px; border: 1px solid #ff0000; background-color: #ffe6e6; color: #cc0000; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Portal de Seguimiento de Envíos</h2>
            <form method="GET" action="/">
                <div class="form-group">
                    <label for="codigo">Código de Rastreo:</label>
                    <input type="text" id="codigo" name="codigo" value="{{ codigo or '' }}" required>
                </div>
                <button type="submit">Buscar</button>
            </form>
            
            {% if resultado %}
                <div class="result">
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
    return render_template_string(template, resultado=resultado, error=error, codigo=codigo)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)