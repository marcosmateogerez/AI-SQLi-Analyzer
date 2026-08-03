import psycopg2
from flask import Flask, request, render_template_string

app = Flask(__name__)

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "user": "postgres",
    "password": "postgres",
    "database": "test_db"
}

def init_db():
    # Intentar crear la base de datos 'test_db' si no existe
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database="postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test_db';")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE DATABASE test_db;")
        cur.close()
        conn.close()
    except Exception:
        pass

    # Crear la tabla e insertar datos de prueba
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100),
                categoria VARCHAR(100),
                precio NUMERIC(10, 2)
            );
        """)
        cur.execute("SELECT COUNT(*) FROM productos;")
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute("""
                INSERT INTO productos (nombre, categoria, precio) VALUES
                ('Manzana', 'Frutas', 1.50),
                ('Plátano', 'Frutas', 0.99),
                ('Leche', 'Lácteos', 1.20),
                ('Queso', 'Lácteos', 3.50),
                ('Pan', 'Panadería', 0.85);
            """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

HTML_TEMPLATE = """
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
        <input type="text" id="categoria" name="categoria" value="{{ categoria_val }}">
        <button type="submit">Buscar</button>
    </form>

    {% if error_msg %}
        <div style="color: red; margin-top: 20px;">
            <h3>Error de Base de Datos:</h3>
            <p>{{ error_msg }}</p>
        </div>
    {% else %}
        <table border="1" style="margin-top: 20px; border-collapse: collapse;">
            <thead>
                <tr>
                    {% for col in columns %}
                        <th style="padding: 8px;">{{ col }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in rows %}
                    <tr>
                        {% for val in row %}
                            <td style="padding: 8px;">{{ val }}</td>
                        {% endfor %}
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    categoria = request.args.get('categoria', '').strip()
    columns = []
    rows = []
    error_msg = None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        if categoria:
            sql_query = "SELECT id, nombre, categoria, precio FROM productos WHERE categoria = %s"
            cur.execute(sql_query, (categoria,))
        else:
            sql_query = "SELECT id, nombre, categoria, precio FROM productos"
            cur.execute(sql_query)
            
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except psycopg2.Error as e:
        error_msg = str(e)

    return render_template_string(
        HTML_TEMPLATE, 
        columns=columns, 
        rows=rows, 
        categoria_val=categoria, 
        error_msg=error_msg
    )

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)