import psycopg2
from flask import Flask, request, render_template_string

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
    try:
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
    except Exception as e:
        print(f"Error al verificar/crear la base de datos: {e}")

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100),
                categoria VARCHAR(100),
                precio NUMERIC(10, 2)
            )
        """)
        conn.commit()

        # Insertar datos de prueba si la tabla está vacía
        cur.execute("SELECT COUNT(*) FROM productos")
        if cur.fetchone()[0] == 0:
            productos_prueba = [
                ('Manzana', 'Frutas', 1.50),
                ('Plátano', 'Frutas', 1.20),
                ('Leche', 'Lácteos', 0.95),
                ('Queso', 'Lácteos', 3.50),
                ('Pan', 'Panadería', 0.80)
            ]
            cur.executemany(
                "INSERT INTO productos (nombre, categoria, precio) VALUES (%s, %s, %s)",
                productos_prueba
            )
            conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al inicializar la tabla o datos: {e}")

@app.route('/')
def index():
    categoria = request.args.get('categoria', '')
    error_message = None
    rows = []
    columns = []

    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        if categoria:
            # Consulta utilizando la estructura de referencia solicitada
            sql_query = f"SELECT id, nombre, categoria, precio FROM productos WHERE categoria = '{categoria}'"
        else:
            sql_query = "SELECT id, nombre, categoria, precio FROM productos"
            
        cur.execute(sql_query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
    except Exception as e:
        error_message = str(e)

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
                <h3>Error en la consulta de base de datos:</h3>
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
        rows=rows, 
        columns=columns, 
        categoria=categoria, 
        error_message=error_message
    )

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)