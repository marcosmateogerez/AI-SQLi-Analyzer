import psycopg2
from flask import Flask, request, render_template_string

app = Flask(__name__)

def init_db():
    # Intentar conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres",
            database="postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()
        try:
            cur.execute("CREATE DATABASE test_db")
        except Exception:
            # Ignorar si la base de datos ya existe
            pass
        cur.close()
        conn.close()
    except Exception:
        pass

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        database="test_db"
    )
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
        cur.execute("""
            INSERT INTO productos (nombre, categoria, precio) VALUES
            ('Manzana', 'Frutas', 1.50),
            ('Plátano', 'Frutas', 0.99),
            ('Leche', 'Lácteos', 1.20),
            ('Queso', 'Lácteos', 3.50),
            ('Pan', 'Panadería', 0.85)
        """)
        
    cur.close()
    conn.close()

@app.route('/')
def index():
    categoria = request.args.get('categoria', '')
    error_msg = None
    rows = []
    colnames = []

    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres",
            database="test_db"
        )
        cur = conn.cursor()

        # Construcción insegura de la consulta SQL mediante concatenación directa (f-string)
        if categoria:
            query = f"SELECT id, nombre, categoria, precio FROM productos WHERE categoria = '{categoria}'"
        else:
            query = "SELECT id, nombre, categoria, precio FROM productos"

        cur.execute(query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        
        cur.close()
        conn.close()
    except Exception as e:
        error_msg = str(e)

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Catálogo de Productos</title>
    </head>
    <body>
        <h1>Catálogo de Productos</h1>
        
        <form method="GET" action="/">
            <label for="categoria">Buscar por Categoría:</label>
            <input type="text" id="categoria" name="categoria" value="{{ categoria }}">
            <button type="submit">Buscar</button>
        </form>
        <br>

        {% if error_msg %}
            <div style="color: red; border: 1px solid red; padding: 10px; background-color: #fdd;">
                <h3>Error de Base de Datos:</h3>
                <p>{{ error_msg }}</p>
            </div>
        {% else %}
            <table border="1" cellpadding="5" cellspacing="0">
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
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(
        html_template, 
        rows=rows, 
        colnames=colnames, 
        error_msg=error_msg, 
        categoria=categoria
    )

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)