import sqlite3
import os
from flask import Flask, request, g, render_template_string

DATABASE = 'datos.db'
app = Flask(__name__)

def get_db():
    """
    Abre una nueva conexión a la base de datos si no hay ninguna para el contexto de la aplicación actual.
    Almacena la conexión en `g` para reutilizarla durante la misma petición.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row # Permite acceder a las columnas por nombre
    return g.db

def close_db(e=None):
    """Cierra la conexión a la base de datos al final de la petición."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """
    Inicializa la base de datos: elimina el archivo existente, lo recrea,
    crea la tabla 'productos' e inserta datos de prueba.
    """
    # Asegura que el archivo de la base de datos se elimine y se recree
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Crear la tabla 'productos'
    cursor.execute("""
        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL
        )
    """)

    # Insertar datos de prueba
    test_products = [
        ('Laptop Gamer', 'Electronica', 1200.00),
        ('Teclado Mecanico', 'Electronica', 85.50),
        ('Silla Ergonomica', 'Muebles', 150.00),
        ('Mesa de Centro', 'Muebles', 75.25),
        ('Libro de Python', 'Libros', 30.00),
        ('Auriculares Bluetooth', 'Electronica', 60.00),
        ('Lampara de Escritorio', 'Iluminacion', 45.99)
    ]
    cursor.executemany("INSERT INTO productos (nombre, categoria, precio) VALUES (?, ?, ?)", test_products)
    conn.commit()
    conn.close()

# Registra la función close_db para que se llame después de cada petición
app.teardown_appcontext(close_db)

@app.route('/', methods=['GET'])
def index():
    db = get_db()
    cursor = db.cursor()
    products = []
    categoria_filtro = request.args.get('categoria')

    if categoria_filtro:
        # Siguiendo estrictamente el estilo de consulta solicitado en el prompt
        query = "SELECT * FROM productos WHERE categoria = '" + categoria_filtro + "'"
        cursor.execute(query)
    else:
        cursor.execute("SELECT * FROM productos")
    
    products = cursor.fetchall()

    # Plantilla HTML incrustada como string
    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Catálogo de Productos</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
            h1 { color: #0056b3; }
            form { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; display: flex; align-items: center; gap: 10px; }
            input[type="text"] { padding: 10px; border: 1px solid #ddd; border-radius: 4px; flex-grow: 1; max-width: 250px; }
            button { padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #f2f2f2; color: #555; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .no-results { text-align: center; color: #888; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>Catálogo de Productos</h1>

        <form action="/" method="GET">
            <label for="categoria">Filtrar por Categoría:</label>
            <input type="text" id="categoria" name="categoria" placeholder="Ej: Electronica" value="{{ categoria_filtro if categoria_filtro else '' }}">
            <button type="submit">Buscar</button>
            <button type="button" onclick="window.location.href='/'">Mostrar Todos</button>
        </form>

        <h2>Resultados {% if categoria_filtro %}(Categoría: "{{ categoria_filtro }}"){% endif %}</h2>
        {% if products %}
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Categoría</th>
                        <th>Precio</th>
                    </tr>
                </thead>
                <tbody>
                    {% for product in products %}
                    <tr>
                        <td>{{ product['id'] }}</td>
                        <td>{{ product['nombre'] }}</td>
                        <td>{{ product['categoria'] }}</td>
                        <td>{{ "%.2f"|format(product['precio']) }} €</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <p class="no-results">No se encontraron productos {% if categoria_filtro %}en la categoría "{{ categoria_filtro }}"{% endif %}.</p>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html_template, products=products, categoria_filtro=categoria_filtro)

if __name__ == '__main__':
    # Inicializa la base de datos y carga los datos de prueba al iniciar la aplicación
    with app.app_context():
        init_db()
    # Ejecuta la aplicación Flask en el host y puerto especificados, con debug=False
    app.run(host='127.0.0.1', port=5000, debug=False)