from flask import Flask, request, render_template_string
import psycopg2

app = Flask(__name__)

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
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
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        password='postgres',
        dbname='test_db'
    )
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            categoria VARCHAR(100) NOT NULL,
            precio NUMERIC(10, 2) NOT NULL
        )
    """)
    conn.commit()

    # Insertar datos de prueba si la tabla está vacía
    cur.execute("SELECT COUNT(*) FROM productos")
    if cur.fetchone()[0] == 0:
        productos_prueba = [
            ('Manzana Roja', 'Frutas', 1.50),
            ('Plátano', 'Frutas', 1.20),
            ('Leche Entera', 'Lácteos', 0.95),
            ('Queso Gouda', 'Lácteos', 5.40),
            ('Pan Integral', 'Panadería', 1.10),
            ('Detergente', 'Limpieza', 3.99)
        ]
        cur.executemany(
            "INSERT INTO productos (nombre, categoria, precio) VALUES (%s, %s, %s)",
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
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
        h1 { color: #333; }
        form { margin-bottom: 20px; }
        input[type="text"] { padding: 8px; width: 250px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 8px 15px; background-color: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #218838; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: white; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #007bff; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .error-box { background-color: #f8d7da; color: #721c24; padding: 15px; border: 1px solid #f5c6cb; border-radius: 4px; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Catálogo de Productos</h1>
    
    <form method="GET" action="/">
        <input type="text" name="categoria" placeholder="Filtrar por categoría..." value="{{ categoria }}">
        <button type="submit">Buscar</button>
    </form>

    {% if error %}
        <div class="error-box">
            <h3>Error de Base de Datos:</h3>
            <p>{{ error }}</p>
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
    {% elif not error %}
        <p>No se encontraron productos.</p>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    categoria = request.args.get('categoria', '')
    rows = []
    colnames = []
    error = None

    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            dbname='test_db'
        )
        cur = conn.cursor()
        
        if categoria:
            # Se utiliza formateo de cadenas directo para permitir la visualización de errores nativos de PostgreSQL ante entradas maliciosas o erróneas
            query = f"SELECT id, nombre, categoria, precio FROM productos WHERE categoria = '{categoria}'"
        else:
            query = "SELECT id, nombre, categoria, precio FROM productos"
            
        cur.execute(query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        
        cur.close()
        conn.close()
    except Exception as e:
        error = str(e)

    return render_template_string(
        HTML_TEMPLATE, 
        categoria=categoria, 
        rows=rows, 
        colnames=colnames, 
        error=error
    )

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)