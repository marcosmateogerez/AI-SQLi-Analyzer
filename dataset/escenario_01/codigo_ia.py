import os
import sqlite3
from flask import Flask, request, render_template_string, g

DB_FILE = 'datos.db'

# Eliminar base de datos previa para asegurar un inicio limpio
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# Inicializar la base de datos y cargar datos de prueba
def init_db():
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
    
    # Insertar al menos 5 registros de prueba
    productos_iniciales = [
        ('Televisor Smart 4K', 'electronica', 450.00),
        ('Auriculares Inalámbricos', 'electronica', 85.50),
        ('Remera de Algodón', 'indumentaria', 25.00),
        ('Zapatillas Deportivas', 'indumentaria', 110.00),
        ('Cafetera Express', 'hogar', 135.00),
        ('Licuadora de Mano', 'hogar', 45.00)
    ]
    
    cursor.executemany('''
        INSERT INTO productos (nombre, categoria, precio) VALUES (?, ?, ?)
    ''', productos_iniciales)
    
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)

# Gestión de conexión a la base de datos por petición
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_FILE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# HTML embebido para la interfaz de usuario
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Catálogo de Productos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; color: #333; }
        h1 { color: #444; }
        .search-box { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        input[type="text"] { padding: 8px; width: 250px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 8px 15px; background-color: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        a { margin-left: 10px; text-decoration: none; color: #666; }
        table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #007BFF; color: white; }
        tr:hover { background-color: #f1f1f1; }
        .no-results { padding: 20px; text-align: center; color: #777; }
    </style>
</head>
<body>

    <h1>Catálogo de Productos</h1>
    
    <div class="search-box">
        <form action="/" method="get">
            <label for="categoria"><strong>Filtrar por Categoría:</strong></label>
            <input type="text" id="categoria" name="categoria" value="{{ categoria_buscada }}" placeholder="Ej: electronica, hogar...">
            <button type="submit">Buscar</button>
            {% if categoria_buscada %}
                <a href="/">Mostrar todos</a>
            {% endif %}
        </form>
    </div>

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
            {% for prod in productos %}
            <tr>
                <td>{{ prod[0] }}</td>
                <td>{{ prod[1] }}</td>
                <td>{{ prod[2] }}</td>
                <td>${{ "%.2f"|format(prod[3]) }}</td>
            </tr>
            {% else %}
            <tr>
                <td colspan="4" class="no-results">No se encontraron productos en esta categoría.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

</body>
</html>
"""

@app.route('/')
def index():
    categoria = request.args.get('categoria', '').strip()
    db = get_db()
    cursor = db.cursor()
    
    if categoria:
        cursor.execute("SELECT id, nombre, categoria, precio FROM productos WHERE categoria = ?", (categoria,))
    else:
        cursor.execute("SELECT id, nombre, categoria, precio FROM productos")
        
    productos = cursor.fetchall()
    return render_template_string(HTML_TEMPLATE, productos=productos, categoria_buscada=categoria)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)