from flask import Flask, request, render_template_string
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

app = Flask(__name__)

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'dbname': 'test_db'
}

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        dbname='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (DB_CONFIG['dbname'],))
    exists = cur.fetchone()
    if not exists:
        cur.execute(f"CREATE DATABASE {DB_CONFIG['dbname']};")
    cur.close()
    conn.close()

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            categoria VARCHAR(100) NOT NULL,
            precio NUMERIC(10, 2) NOT NULL
        );
    """)
    conn.commit()

    # Insertar datos de prueba si la tabla está vacía
    cur.execute("SELECT COUNT(*) FROM productos;")
    if cur.fetchone()[0] == 0:
        productos_prueba = [
            ('Leche Entera', 'Lácteos', 1.20),
            ('Yogur Natural', 'Lácteos', 0.90),
            ('Manzana Gala', 'Frutas', 2.30),
            ('Plátano de Canarias', 'Frutas', 1.70),
            ('Pan de Molde', 'Panadería', 1.45),
            ('Croissant', 'Panadería', 0.85)
        ]
        cur.executemany(
            "INSERT INTO productos (nombre, categoria, precio) VALUES (%s, %s, %s);",
            productos_prueba
        )
        conn.commit()
    cur.close()
    conn.close()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Catálogo de Supermercado</title>
    <style>
        body { font-family: sans-serif; margin: 40px; background-color: #f4f4f9; }
        h1 { color: #333; }
        form { margin-bottom: 20px; }
        input[type="text"] { padding: 8px; width: 250px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 8px 15px; background-color: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: white; }
        th, td { border: 1px solid #dddddd; text-align: left; padding: 12px; }
        th { background-color: #f2f2f2; }
        .error-box { padding: 15px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 4px; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Catálogo de Productos</h1>
    
    <form method="GET" action="/">
        <input type="text" name="categoria" placeholder="Filtrar por categoría..." value="{{ categoria }}">
        <button type="submit">Filtrar</button>
    </form>

    {% if error %}
        <div class="error-box">
            <strong>Error de Base de Datos:</strong> {{ error }}
        </div>
    {% else %}
        <table>
            <thead>
                <tr>
                    {% for col in columnas %}
                        <th>{{ col }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for fila in filas %}
                    <tr>
                        {% for valor in fila %}
                            <td>{{ valor }}</td>
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
    columnas = []
    filas = []
    error = None
    conn = None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        if categoria:
            query = "SELECT id, nombre, categoria, precio FROM productos WHERE categoria ILIKE %s;"
            cur.execute(query, (categoria,))
        else:
            query = "SELECT id, nombre, categoria, precio FROM productos;"
            cur.execute(query)
            
        columnas = [desc[0] for desc in cur.description]
        filas = cur.fetchall()
        cur.close()
    except Exception as e:
        error = str(e)
    finally:
        if conn:
            conn.close()

    return render_template_string(
        HTML_TEMPLATE, 
        columnas=columnas, 
        filas=filas, 
        categoria=categoria, 
        error=error
    )

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)