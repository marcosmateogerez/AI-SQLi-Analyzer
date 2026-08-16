from flask import Flask, request, render_template_string
import psycopg2

DB_CONFIG = {
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
    try:
        cur.execute("CREATE DATABASE test_db")
    except Exception:
        # La base de datos ya existe
        pass
    finally:
        cur.close()
        conn.close()

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    conn = psycopg2.connect(**DB_CONFIG)
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
    
    # Verificar si la tabla está vacía
    cur.execute("SELECT COUNT(*) FROM productos")
    if cur.fetchone()[0] == 0:
        datos_prueba = [
            ('Manzana', 'Frutas', 1.50),
            ('Plátano', 'Frutas', 1.20),
            ('Leche', 'Lácteos', 0.99),
            ('Queso', 'Lácteos', 3.50),
            ('Pan', 'Panadería', 0.85)
        ]
        for nombre, categoria, precio in datos_prueba:
            cur.execute(
                "INSERT INTO productos (nombre, categoria, precio) VALUES (%s, %s, %s)",
                (nombre, categoria, precio)
            )
            
    cur.close()
    conn.close()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    categoria = request.args.get('categoria', '')
    error_message = None
    rows = []
    colnames = []
    
    # Construcción insegura de la consulta SQL mediante f-strings (concatenación directa)
    if categoria:
        query = f"SELECT id, nombre, categoria, precio FROM productos WHERE categoria = '{categoria}'"
    else:
        query = "SELECT id, nombre, categoria, precio FROM productos"
        
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
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
            .error { color: red; background-color: #ffe6e6; padding: 15px; border: 1px solid red; margin-top: 20px; }
            .search-box { margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>Catálogo de Productos - Supermercado</h1>
        
        <div class="search-box">
            <form method="GET" action="/">
                <label for="categoria">Filtrar por Categoría:</label>
                <input type="text" id="categoria" name="categoria" value="{{ categoria }}">
                <button type="submit">Buscar</button>
            </form>
        </div>

        {% if error_message %}
            <div class="error">
                <h3>Error de Base de Datos (PostgreSQL):</h3>
                <pre>{{ error_message }}</pre>
            </div>
        {% endif %}

        {% if rows %}
            <table>
                <thead>
                    <tr>
                        {% for col in colnames %}
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
        {% elif not error_message %}
            <p>No se encontraron productos.</p>
        {% endif %}
    </body>
    </html>
    """
    
    return render_template_string(
        html_template, 
        categoria=categoria, 
        rows=rows, 
        colnames=colnames, 
        error_message=error_message
    )

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)