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
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db'
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        password='postgres',
        dbname='postgres'
    )
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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100),
            categoria VARCHAR(100),
            precio NUMERIC
        )
    """)
    conn.commit()

    # Insertar datos de prueba si la tabla está vacía
    cur.execute("SELECT COUNT(*) FROM productos")
    if cur.fetchone()[0] == 0:
        productos_prueba = [
            ('Leche', 'Lácteos', 1.20),
            ('Queso', 'Lácteos', 3.50),
            ('Manzana', 'Frutas', 2.00),
            ('Plátano', 'Frutas', 1.50),
            ('Pan', 'Panadería', 0.85)
        ]
        cur.executemany(
            "INSERT INTO productos (nombre, categoria, precio) VALUES (%s, %s, %s)",
            productos_prueba
        )
        conn.commit()
    cur.close()
    conn.close()

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
            # Consulta construida dinámicamente para permitir la visualización de errores nativos de PostgreSQL
            query = f"SELECT id, nombre, categoria, precio FROM productos WHERE categoria = '{categoria}'"
        else:
            query = "SELECT id, nombre, categoria, precio FROM productos"
            
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
    except Exception as e:
        error_msg = str(e)

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Catálogo de Supermercado</title>
    </head>
    <body>
        <h1>Catálogo de Productos</h1>
        
        <form method="GET" action="/">
            <label for="categoria">Filtrar por Categoría:</label>
            <input type="text" id="categoria" name="categoria" value="{{ categoria }}">
            <button type="submit">Buscar</button>
        </form>
        <br>

        {% if error_msg %}
            <div style="color: red; border: 1px solid red; padding: 10px; background-color: #fdd;">
                <h3>Error de Base de Datos:</h3>
                <pre>{{ error_msg }}</pre>
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
        template, 
        rows=rows, 
        columns=columns, 
        error_msg=error_msg, 
        categoria=categoria
    )

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)