from flask import Flask, request, render_template_string
import psycopg2

app = Flask(__name__)

def get_db_connection(dbname='test_db'):
    return psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        password='postgres',
        dbname=dbname
    )

def init_db():
    # Intentar crear la base de datos 'test_db' si no existe
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            dbname='postgres'
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

    # Crear la tabla e insertar datos de prueba
    try:
        conn = get_db_connection()
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
                ('Leche Entera', 'Lácteos', 1.20),
                ('Queso Gouda', 'Lácteos', 4.50),
                ('Manzana Gala', 'Frutas', 1.80),
                ('Plátano de Canarias', 'Frutas', 1.40),
                ('Pan de Molde', 'Panadería', 1.10),
                ('Croissant', 'Panadería', 0.85)
            ]
            cur.executemany(
                "INSERT INTO productos (nombre, categoria, precio) VALUES (%s, %s, %s)",
                productos_prueba
            )
            conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al inicializar la tabla de productos: {e}")

@app.route('/')
def index():
    categoria = request.args.get('categoria', '')
    error_msg = None
    rows = []
    columns = []

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if categoria:
            # Consulta vulnerable de forma intencionada para permitir la visualización de errores nativos de PostgreSQL
            query = f"SELECT id, nombre, categoria, precio FROM productos WHERE categoria = '{categoria}'"
            cur.execute(query)
        else:
            cur.execute("SELECT id, nombre, categoria, precio FROM productos")
        
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
    except Exception as e:
        error_msg = str(e)

    template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Catálogo de Productos</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }
            th { background-color: #f2f2f2; }
            .error-box { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 15px; margin-top: 20px; border-radius: 4px; }
            .search-box { margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>Catálogo de Productos - Supermercado</h1>
        
        <div class="search-box">
            <form method="GET" action="/">
                <label for="categoria">Filtrar por Categoría: </label>
                <input type="text" id="categoria" name="categoria" value="{{ categoria }}">
                <button type="submit">Buscar</button>
            </form>
        </div>

        {% if error_msg %}
            <div class="error-box">
                <h3>Error de Base de Datos (PostgreSQL):</h3>
                <pre>{{ error_msg }}</pre>
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
    return render_template_string(template, rows=rows, columns=columns, error_msg=error_msg, categoria=categoria)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)