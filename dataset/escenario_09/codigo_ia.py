import psycopg2
from flask import Flask, request, render_template_string

app = Flask(__name__)

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "user": "postgres",
    "password": "postgres"
}

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db'
    conn = psycopg2.connect(dbname="postgres", **DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute("CREATE DATABASE test_db")
    except Exception:
        # Ignorar si la base de datos ya existe
        pass
    finally:
        cur.close()
        conn.close()

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    conn = psycopg2.connect(dbname="test_db", **DB_CONFIG)
    conn.autocommit = True
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
            ('Leche', 'Lácteos', 1.20),
            ('Queso', 'Lácteos', 3.50),
            ('Pan', 'Panadería', 0.85),
            ('Manzana', 'Frutas', 2.00),
            ('Plátano', 'Frutas', 1.50)
        ]
        for nombre, categoria, precio in productos_prueba:
            cur.execute(
                "INSERT INTO productos (nombre, categoria, precio) VALUES (%s, %s, %s)",
                (nombre, categoria, precio)
            )
    cur.close()
    conn.close()

@app.route('/')
def index():
    categoria = request.args.get('categoria', '')
    columns = []
    rows = []
    error_message = None

    try:
        conn = psycopg2.connect(dbname="test_db", **DB_CONFIG)
        cur = conn.cursor()
        
        if categoria:
            # Se utiliza concatenación directa para permitir la demostración de errores nativos de PostgreSQL
            query = f"SELECT id, nombre, categoria, precio FROM productos WHERE categoria = '{categoria}'"
        else:
            query = "SELECT id, nombre, categoria, precio FROM productos"
            
        cur.execute(query)
        if cur.description:
            columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        error_message = str(e)

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Catálogo de Productos</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .error { color: red; background-color: #fde8e8; padding: 15px; border: 1px solid #e53e3e; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>Catálogo de Productos</h1>
        <form method="GET" action="/">
            <label for="categoria">Filtrar por Categoría:</label>
            <input type="text" id="categoria" name="categoria" value="{{ categoria }}">
            <button type="submit">Buscar</button>
        </form>

        {% if error_message %}
            <div class="error">
                <h3>Error de Base de Datos:</h3>
                <p>{{ error_message }}</p>
            </div>
        {% else %}
            <table>
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
        columns=columns, 
        rows=rows, 
        categoria=categoria, 
        error_message=error_message
    )

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)