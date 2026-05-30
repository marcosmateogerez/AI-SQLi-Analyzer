import os
import sqlite3
from flask import Flask, request, g, render_template_string

DATABASE = 'biblioteca.db'

# Eliminar la base de datos existente al iniciar el script para recrearla limpia
if os.path.exists(DATABASE):
    os.remove(DATABASE)

# Inicializar la base de datos y cargar los datos de prueba
def inicializar_base_de_datos():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            anio INTEGER NOT NULL
        )
    ''')
    
    libros_iniciales = [
        ('Ficciones', 'Jorge Luis Borges', 1944),
        ('Cien años de soledad', 'Gabriel García Márquez', 1967),
        ('Pedro Páramo', 'Juan Rulfo', 1955),
        ('Rayuela', 'Julio Cortázar', 1963),
        ('Don Quijote de la Mancha', 'Miguel de Cervantes', 1605)
    ]
    
    cursor.executemany(
        'INSERT INTO libros (titulo, autor, anio) VALUES (?, ?, ?)', 
        libros_iniciales
    )
    conn.commit()
    conn.close()

inicializar_base_de_datos()

app = Flask(__name__)

# Gestión segura de la conexión a la base de datos por petición (multi-hilo)
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Plantilla HTML única para la interfaz web
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventario de Biblioteca</title>
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
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 20px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }
        form {
            margin-bottom: 30px;
            display: flex;
            gap: 10px;
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
        }
        button:hover {
            background-color: #2980b9;
        }
        a.clear-btn {
            padding: 10px 20px;
            background-color: #95a5a6;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 16px;
            display: inline-block;
        }
        a.clear-btn:hover {
            background-color: #7f8c8d;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
            color: #2c3e50;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        .no-results {
            color: #e74c3c;
            font-weight: bold;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Inventario de la Biblioteca</h1>
        
        <form action="/" method="get">
            <input type="text" name="autor" placeholder="Buscar por autor..." value="{{ autor_buscado }}">
            <button type="submit">Buscar</button>
            {% if autor_buscado %}
                <a href="/" class="clear-btn">Mostrar Todos</a>
            {% endif %}
        </form>

        <h2>Resultados</h2>
        {% if libros %}
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Título</th>
                        <th>Autor</th>
                        <th>Año</th>
                    </tr>
                </thead>
                <tbody>
                    {% for libro in libros %}
                        <tr>
                            <td>{{ libro['id'] }}</td>
                            <td>{{ libro['titulo'] }}</td>
                            <td>{{ libro['autor'] }}</td>
                            <td>{{ libro['anio'] }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <p class="no-results">No se encontraron libros que coincidan con la búsqueda.</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    autor_buscado = request.args.get('autor', '').strip()
    db = get_db()
    cursor = db.cursor()
    
    if autor_buscado:
        # Búsqueda parcial insensible a mayúsculas/minúsculas usando LIKE
        cursor.execute(
            "SELECT id, titulo, autor, anio FROM libros WHERE autor LIKE ?", 
            (f"%{autor_buscado}%",)
        )
    else:
        cursor.execute("SELECT id, titulo, autor, anio FROM libros")
        
    libros = cursor.fetchall()
    return render_template_string(
        HTML_TEMPLATE, 
        libros=libros, 
        autor_buscado=autor_buscado
    )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)