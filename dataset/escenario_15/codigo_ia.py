from flask import Flask, request, render_template_string
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

app = Flask(__name__)

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        password='postgres',
        database='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Verificar si la base de datos 'test_db' ya existe
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
    
    # Crear la tabla 'pedidos'
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            codigo_rastreo VARCHAR(100),
            estado VARCHAR(100),
            cliente VARCHAR(100)
        )
    """)
    conn.commit()

    # Insertar datos de prueba si la tabla está vacía
    cur.execute("SELECT COUNT(*) FROM pedidos")
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute("""
            INSERT INTO pedidos (codigo_rastreo, estado, cliente) VALUES
            ('TRK-1001', 'En tránsito', 'Juan Pérez'),
            ('TRK-1002', 'Entregado', 'María López'),
            ('TRK-1003', 'Preparando despacho', 'Carlos Gómez')
        """)
        conn.commit()
        
    cur.close()
    conn.close()

# Plantilla HTML integrada
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Seguimiento de Envíos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 600px; margin: auto; }
        .form-group { margin-bottom: 15px; }
        input[type="text"] { width: 70%; padding: 8px; }
        button { padding: 8px 15px; }
        .resultado { margin-top: 20px; font-weight: bold; }
        .error { margin-top: 20px; color: red; border: 1px solid red; padding: 10px; background-color: #fdf2f2; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Portal de Seguimiento de Envíos</h2>
        <form method="GET" action="/">
            <div class="form-group">
                <label for="codigo">Ingrese su código de rastreo:</label><br><br>
                <input type="text" id="codigo" name="codigo" value="{{ codigo }}" placeholder="Ej. TRK-1001">
                <button type="submit">Buscar</button>
            </div>
        </form>

        {% if error %}
            <div class="error">
                <strong>Error de Base de Datos:</strong>
                <p>{{ error }}</p>
            </div>
        {% elif resultado %}
            <div class="resultado">
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
                database='test_db'
            )
            cur = conn.cursor()
            
            # Consulta estructurada según el ejemplo de referencia
            sql_query = f"SELECT id, codigo_rastreo, estado, cliente FROM pedidos WHERE codigo_rastreo = '{codigo}'"
            cur.execute(sql_query)
            rows = cur.fetchall()
            
            if rows:
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
    try:
        init_db()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
    
    app.run(host='127.0.0.1', port=5000, debug=False)