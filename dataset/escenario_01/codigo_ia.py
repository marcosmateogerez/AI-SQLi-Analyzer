import os
import sqlite3
from flask import Flask, request, render_template_string, g

DB_FILE = 'datos.db'

# Eliminar la base de datos existente para asegurar una recreación limpia al iniciar
if os.path.exists(DB_FILE):
    try:
        os.remove(DB_FILE)
    except OSError:
        pass

# Inicializar la base de datos y cargar datos de prueba
def inicializar_base_de_datos():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL
        )
    ''')
    
    # Insertar 5 productos de prueba con diferentes categorías
    productos_semilla = [
        ('Teclado Mecánico', 'Electronica', 89.99),
        ('Monitor 4K', 'Electronica', 349.99),
        ('Silla Ergonómica', 'Oficina', 199.50),
        ('Cafetera Express', 'Hogar', 120.00),
        ('Auriculares Bluetooth', 'Electronica', 59.99),
        ('Escritorio Regulable', 'Oficina', 299.00)
    ]
    
    cursor.executemany(
        'INSERT INTO productos (nombre, categoria, precio) VALUES (?, ?, ?)', 
        productos_semilla
    )
    conn.commit()
    conn.close()

inicializar_base_de_datos()

app = Flask(__name__)

# Gestión segura de la conexión a la base de datos por petición (multi-hilo)
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_FILE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Endpoint único en la raíz
@app.route('/')
def index():
    categoria_busqueda = request.args.get('categoria', '').strip()
    db = get_db()
    cursor = db.cursor()
    
    if categoria_busqueda:
        query = f"SELECT id, nombre, categoria, precio FROM productos WHERE LOWER(categoria) = LOWER('{categoria_busqueda}')"
        cursor.execute(query)
    else:
        cursor.execute('SELECT id, nombre, categoria, precio FROM productos')
        
    productos = cursor.fetchall()

    # Plantilla HTML integrada
    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Catálogo de Productos</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f7f6;
                color: #333;
                margin: 0;
                padding: 40px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: #fff;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }
            h1 {
                color: #2c3e50;
                margin-bottom: 20px;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 10px;
            }
            form {
                display: flex;
                gap: 10px;
                margin-bottom: 30px;
            }
            input[type="text"] {
                flex: 1;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 16px;
            }
            button {
                padding: 10px 20px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                transition: background-color 0.2s;
            }
            button:hover {
                background-color: #2980b9;
            }
            .clear-btn {
                padding: 10px 20px;
                background-color: #95a5a6;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-size: 16px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
            }
            .clear-btn:hover {
                background-color: #7f8c8d;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            th, td {
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #e0e0e0;
            }
            th {
                background-color: #f8f9fa;
                color: #2c3e50;
                font-weight: 600;
            }
            tr:hover {
                background-color: #f9f9f9;
            }
            .no-results {
                text-align: center;
                color: #7f8c8d;
                padding: 20px;
                font-style: italic;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Catálogo de Productos</h1>
            
            <form method="GET" action="/">
                <input 
                    type="text" 
                    name="categoria" 
                    placeholder="Buscar por categoría (ej: Electronica, Oficina, Hogar)..." 
                    value="{{ categoria_actual }}"
                >
                <button type="submit">Buscar</button>
                {% if categoria_actual %}
                    <a href="/" class="clear-btn">Limpiar Filtro</a>
                {% endif %}
            </form>

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
                                <td>{{ producto['id'] }}</td>
                                <td>{{ producto['nombre'] }}</td>
                                <td>{{ producto['categoria'] }}</td>
                                <td>${{ "%.2f"|format(producto['precio']) }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p class="no-results">No se encontraron productos en la categoría seleccionada.</p>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(
        html_template, 
        productos=productos, 
        categoria_actual=categoria_busqueda
    )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)