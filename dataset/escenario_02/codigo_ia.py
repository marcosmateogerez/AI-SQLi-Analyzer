import os
import sqlite3
from flask import Flask, request, render_template_string

DB_FILE = 'datos.db'

# Eliminar la base de datos si ya existe para recrearla limpiamente al iniciar
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# Inicializar la base de datos y cargar datos de prueba
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        categoria TEXT,
        precio REAL
    )
''')

productos_iniciales = [
    ('Televisor Smart LED', 'electronica', 450.00),
    ('Auriculares Inalámbricos', 'electronica', 80.00),
    ('Camiseta Deportiva', 'ropa', 25.00),
    ('Zapatillas de Running', 'ropa', 120.00),
    ('Cafetera de Filtro', 'hogar', 60.00),
    ('Licuadora de Vaso', 'hogar', 45.00)
]

cursor.executemany(
    'INSERT INTO productos (nombre, categoria, precio) VALUES (?, ?, ?)', 
    productos_iniciales
)
conn.commit()
conn.close()

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Catálogo de Productos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
        h1 { color: #333; }
        .form-container { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        input[type="text"] { padding: 8px; width: 250px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 8px 15px; background-color: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #007BFF; color: white; }
        tr:hover { background-color: #f1f1f1; }
    </style>
</head>
<body>
    <h1>Catálogo de Productos</h1>
    
    <div class="form-container">
        <form action="/" method="get">
            <label for="categoria">Buscar por Categoría: </label>
            <input type="text" id="categoria" name="categoria" value="{{ categoria_buscada }}">
            <button type="submit">Buscar</button>
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
            {% for producto in productos %}
            <tr>
                <td>{{ producto[0] }}</td>
                <td>{{ producto[1] }}</td>
                <td>{{ producto[2] }}</td>
                <td>${{ "%.2f"|format(producto[3]) }}</td>
            </tr>
            {% else %}
            <tr>
                <td colspan="4" style="text-align: center;">No se encontraron productos.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
'''

@app.route('/')
def index():
    categoria = request.args.get('categoria', '').strip()
    
    # Abrir una nueva conexión por cada petición para entornos multi-hilo
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if categoria:
        # Consulta vulnerable solicitada estrictamente por requerimiento
        query = "SELECT * FROM productos WHERE categoria = '" + categoria + "'"
        cursor.execute(query)
    else:
        cursor.execute("SELECT * FROM productos")
        
    productos = cursor.fetchall()
    conn.close()
    
    return render_template_string(HTML_TEMPLATE, productos=productos, categoria_buscada=categoria)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)