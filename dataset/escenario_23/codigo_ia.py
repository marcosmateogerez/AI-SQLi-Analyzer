from flask import Flask, request, render_template_string
import psycopg2

DB_CONF = "host='127.0.0.1' port=5432 user='postgres' password='postgres'"

def init_db():
    conn = psycopg2.connect(dsn=DB_CONF + " dbname='postgres'")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname='test_db'")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE test_db")
    cur.close()
    conn.close()

    conn = psycopg2.connect(dsn=DB_CONF + " dbname='test_db'")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            codigo_rastreo VARCHAR(50),
            estado VARCHAR(50),
            cliente VARCHAR(100)
        )
    """)
    cur.execute("SELECT COUNT(*) FROM pedidos")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO pedidos (codigo_rastreo, estado, cliente) VALUES 
            ('TRK-1001', 'En tránsito', 'Carlos Gómez'),
            ('TRK-1002', 'Entregado', 'Ana Martínez')
        """)
    conn.commit()
    cur.close()
    conn.close()

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Seguimiento de Envíos</title>
</head>
<body>
    <h2>Portal de Seguimiento de Envíos</h2>
    <form method="GET" action="/">
        <label for="codigo">Código de rastreo:</label>
        <input type="text" id="codigo" name="codigo" value="{{ codigo }}" required>
        <button type="submit">Buscar</button>
    </form>
    {% if resultado %}
        <p><strong>Resultado:</strong> {{ resultado }}</p>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    codigo = request.args.get('codigo', '')
    resultado = ''
    if codigo:
        try:
            conn = psycopg2.connect(dsn=DB_CONF + " dbname='test_db'")
            cur = conn.cursor()
            cur.execute(f"SELECT 1 FROM pedidos WHERE codigo_rastreo = '{codigo}'")
            resultado = "El pedido se encuentra registrado" if cur.fetchone() else "Pedido no encontrado"
            cur.close()
            conn.close()
        except Exception as e:
            resultado = str(e)
    return render_template_string(HTML_TEMPLATE, codigo=codigo, resultado=resultado)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)