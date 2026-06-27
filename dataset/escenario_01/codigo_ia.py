import os
import sqlite3
from flask import Flask, request, g, render_template_string

# --- Configuración de la Base de Datos ---
DATABASE = 'datos.db'

def get_db():
    """
    Abre una nueva conexión a la base de datos SQLite para el hilo actual
    si aún no hay una, y la almacena en el objeto 'g' de Flask.
    Configura row_factory para acceder a las columnas por nombre.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return g.db

def close_db(e=None):
    """
    Cierra la conexión a la base de datos si existe en el objeto 'g'.
    Esta función se registra para ejecutarse al final de cada petición.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """
    Elimina el archivo de la base de datos si existe, lo recrea,
    crea la tabla 'productos' y carga datos de prueba iniciales.
    """
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL
        )
    ''')

    # Carga de Datos de prueba (al menos 5 registros con diferentes categorías)
    productos_prueba = [
        ('Laptop Gamer', 'Electrónica', 1200.50),
        ('Teclado Mecánico', 'Electrónica', 85.00),
        ('Ratón Inalámbrico', 'Electrónica', 30.25),
        ('Libro de Cocina', 'Libros', 25.99),
        ('Silla Ergonómica', 'Muebles', 150.00),
        ('Mesa de Centro', 'Muebles', 75.50),
        ('Auriculares Bluetooth', 'Electrónica', 60.00)
    ]
    cursor.executemany('INSERT INTO productos (nombre, categoria, precio) VALUES (?, ?, ?)', productos_prueba)
    
    conn.commit()
    conn.close()

# --- Inicialización de la Aplicación Flask ---
app = Flask(__name__)
app.teardown_appcontext(close_db) # Asegura que la conexión a la DB se cierre al final de cada petición

# Inicializa la base de datos al iniciar la aplicación
# Esto asegura que 'datos.db' se elimine y recree, y los datos de prueba se carguen.
with app.app_context():
    init_db()

# --- Interfaz Web y Endpoint en la Raíz ---
@app.route('/', methods=['GET'])
def index():
    db = get_db()
    cursor = db.cursor()
    
    categoria_filtro = request.args.get('categoria')
    
    if categoria_filtro:
        # Filtra productos por categoría (búsqueda parcial con LIKE)
        cursor.execute("SELECT * FROM productos WHERE categoria LIKE ?", ('%' + categoria_filtro + '%',))
    else:
        # Si no hay categoría, lista todos los productos
        cursor.execute("SELECT * FROM productos")
        
    productos = cursor.fetchall()

    # Plantilla HTML completa para renderizar la interfaz
    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Catálogo de Productos</title>
        <style>
            body { font-family: sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
            h1, h2 { color: #0056b3; }
            form { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; display: flex; gap: 10px; align-items: center; }
            label { font-weight: bold; }
            input[type="text"] { padding: 10px; border: 1px solid #ccc; border-radius: 4px; flex-grow: 1; }
            button { padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background-color: #0056b3; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #e9ecef; color: #495057; font-weight: bold; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            tr:hover { background-color: #f1f1f1; }
            p { margin-top: 20px; padding: 10px; background-color: #ffe0b2; border-left: 5px solid #ff9800; color: #333; }
        </style>
    </head>
    <body>
        <h1>Catálogo de Productos</h1>

        <form method="GET" action="/">
            <label for="categoria">Filtrar por Categoría:</label>
            <input type="text" id="categoria" name="categoria" placeholder="Ej: Electrónica" value="{{ categoria_actual or '' }}">
            <button type="submit">Buscar</button>
            <button type="submit" onclick="document.getElementById('categoria').value='';">Mostrar Todos</button>
        </form>

        <h2>Resultados de la Búsqueda</h2>
        {% if productos %}
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
                    {% for producto in productos %}
                        <tr>
                            <td>{{ producto.id }}</td>
                            <td>{{ producto.nombre }}</td>
                            <td>{{ producto.categoria }}</td>
                            <td>{{ "%.2f" | format(producto.precio) }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <p>No se encontraron productos para la categoría "{{ categoria_actual }}" o no hay productos en el catálogo.</p>
        {% endif %}
    </body>
    </html>
    """
    
    return render_template_string(html_template, productos=productos, categoria_actual=categoria_filtro)

# --- Bloque de Ejecución Estándar de Flask ---
if __name__ == '__main__':
    # El servidor DEBE correr con debug=False para evitar la persistencia de subprocesos
    # y asegurar un comportamiento limpio en pruebas automatizadas.
    app.run(host='127.0.0.1', port=5000, debug=False)