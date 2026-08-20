import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask, request, render_template_string

app = Flask(__name__)

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "user": "postgres",
    "password": "postgres"
}
DB_NAME = "test_db"

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    conn = psycopg2.connect(dbname="postgres", **DB_CONFIG)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
    exists = cur.fetchone()
    if not exists:
        cur.execute(f"CREATE DATABASE {DB_NAME}")
    
    cur.close()
    conn.close()

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    conn = psycopg2.connect(dbname=DB_NAME, **DB_CONFIG)
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
        productos_prueba = [
            ('Manzana', 'Frutas', 1.50),
            ('Plátano', 'Frutas', 1.20),
            ('Leche', 'Lácteos', 0.99),
            ('Queso', 'Lácteos', 2.50),
            ('Pan', 'Panadería', 0.85)
        ]
        for nombre, categoria, precio in productos_prueba:
            cur.execute(
                "INSERT INTO productos (nombre, categoria, precio) VALUES (%s, %s, %s)",
                (nombre, categoria, precio)
            )
    
    conn.commit()
    cur.close()
    conn.close()

@app.route('/', methods=['GET'])
def index():
    categoria = request.args.get('categoria', '')
    columns = []
    rows = []
    error_message = None

    if categoria:
        sql_query = f"SELECT id, nombre, categoria, precio FROM productos WHERE categoria = '{categoria}'"
    else:
        sql_query = "SELECT id, nombre, categoria, precio FROM productos"

    conn = None
    try:
        conn = psycopg2.connect(dbname=DB_NAME, **DB_CONFIG)
        cur = conn.cursor()
        cur.execute(sql_query)
        if cur.description:
            columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        cur.close()
    except Exception as e:
        error_message = str(e)
    finally:
        if conn:
            conn.close()

    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Catálogo de Productos</title>
    </head>
    <body>
        <h1>Catálogo de Productos</h1>
        
        <form method="GET" action="/">
            <label for="categoria">Filtrar por Categoría:</label>
            <input type="text" id="categoria" name="categoria" value="{{ categoria }}">
            <button type="submit">Buscar</button>
        </form>
        
        <br>

        {% if error_message %}
            <div style="color: red; border: 1px solid red; padding: 10px; background-color: #f8d7da;">
                <h3>Error de Base de Datos:</h3>
                <pre>{{ error_message }}</pre>
            </div>
        {% else %}
            <table border="1" cellpadding="5" cellspacing="0">
                <thead>
                    <tr>
                        {% for col in columns %}
                            <th>{{ col }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                        <tr>
                            {% for val in row %}
                                <td>{{ val }}</td>
                            {% endfor %}
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endif %}
    </body>
    </html>
    """

    return render_template_string(
        html_template,
        categoria=categoria,
        columns=columns,
        rows=rows,
        error_message=error_message
    )

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)