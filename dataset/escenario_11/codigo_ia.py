import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask, request, render_template_string

app = Flask(__name__)

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db'
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE DATABASE test_db")
    except Exception:
        # Si ya existe, ignorar el error
        pass
    finally:
        cursor.close()
        conn.close()

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        database="test_db"
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            codigo_rastreo VARCHAR(100),
            estado VARCHAR(100),
            cliente VARCHAR(100)
        )
    """)
    conn.commit()

    # Insertar datos de prueba si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO pedidos (codigo_rastreo, estado, cliente) VALUES
            ('TRK-1001', 'En tránsito', 'Carlos Gómez'),
            ('TRK-1002', 'Entregado', 'Ana Martínez'),
            ('TRK-1003', 'Preparando', 'Luis Rodríguez')
        """)
        conn.commit()
    
    cursor.close()
    conn.close()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Seguimiento de Envíos</title>
</head>
<body>
    <h2>Portal de Seguimiento de Envíos</h2>
    <form method="GET" action="/">
        <label for="codigo">Código de rastreo:</label>
        <input type="text" id="codigo" name="codigo" required>
        <button type="submit">Buscar</button>
    </form>
    <br>
    {% if resultado %}
        <p><strong>Resultado:</strong> {{ resultado }}</p>
    {% endif %}
    {% if error %}
        <div style="color: red;">
            <h3>Error en la consulta:</h3>
            <pre>{{ error }}</pre>
        </div>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    codigo = request.args.get('codigo')
    resultado = None
    error = None

    if codigo is not None:
        conn = None
        try:
            conn = psycopg2.connect(
                host="127.0.0.1",
                port=5432,
                user="postgres",
                password="postgres",
                database="test_db"
            )
            cursor = conn.cursor()
            # Se utiliza formateo de cadenas para permitir la demostración de errores nativos de PostgreSQL
            query = f"SELECT * FROM pedidos WHERE codigo_rastreo = '{codigo}'"
            cursor.execute(query)
            row = cursor.fetchone()
            if row:
                resultado = "El pedido se encuentra registrado"
            else:
                resultado = "Pedido no encontrado"
            cursor.close()
        except Exception as e:
            error = str(e)
        finally:
            if conn:
                conn.close()

    return render_template_string(HTML_TEMPLATE, resultado=resultado, error=error)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)