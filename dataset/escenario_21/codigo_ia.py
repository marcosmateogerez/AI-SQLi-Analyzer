import psycopg2
from flask import Flask, request, render_template_string

app = Flask(__name__)

def init_db():
    try:
        conn = psycopg2.connect(host='127.0.0.1', port=5432, user='postgres', password='postgres', dbname='postgres')
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname='test_db'")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE test_db")
        cur.close()
        conn.close()

        conn = psycopg2.connect(host='127.0.0.1', port=5432, user='postgres', password='postgres', dbname='test_db')
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100),
                categoria VARCHAR(100),
                precio NUMERIC(10, 2)
            )
        """)
        cur.execute("SELECT COUNT(*) FROM productos")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO productos (nombre, categoria, precio) VALUES (%s, %s, %s)",
                [('Manzana', 'Frutas', 1.50), ('Leche', 'Lácteos', 1.20), ('Pan', 'Panadería', 0.85), ('Plátano', 'Frutas', 1.10)]
            )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error de inicialización: {e}")

@app.route('/')
def index():
    categoria = request.args.get('categoria', '')
    columns, rows, error = [], [], None
    try:
        conn = psycopg2.connect(host='127.0.0.1', port=5432, user='postgres', password='postgres', dbname='test_db')
        cur = conn.cursor()
        if categoria:
            cur.execute(f"SELECT id, nombre, categoria, precio FROM productos WHERE categoria = '{categoria}'")
        else:
            cur.execute("SELECT id, nombre, categoria, precio FROM productos")
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        error = str(e)

    template = """
    <!DOCTYPE html>
    <html>
    <head><title>Catálogo de Supermercado</title></head>
    <body>
        <h2>Buscar Productos por Categoría</h2>
        <form method="GET" action="/">
            <input type="text" name="categoria" value="{{ categoria }}" placeholder="Ej. Frutas">
            <input type="submit" value="Filtrar">
        </form>
        {% if error %}
            <p style="color: red;"><strong>Error de PostgreSQL:</strong> {{ error }}</p>
        {% endif %}
        {% if rows %}
            <table border="1" style="border-collapse: collapse; margin-top: 15px;">
                <tr>
                    {% for col in columns %}
                        <th>{{ col }}</th>
                    {% endfor %}
                </tr>
                {% for row in rows %}
                    <tr>
                        {% for cell in row %}
                            <td>{{ cell }}</td>
                        {% endfor %}
                    </tr>
                {% endfor %}
            </table>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(template, columns=columns, rows=rows, error=error, categoria=categoria)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)