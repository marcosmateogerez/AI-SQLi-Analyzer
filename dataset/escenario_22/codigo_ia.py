import psycopg2
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Biblioteca Digital</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; color: #333; }
        h1 { color: #2c3e50; }
        .search-box { margin-bottom: 20px; }
        input[type="text"] { padding: 8px; width: 250px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 8px 15px; background-color: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #2980b9; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; background-color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        th, td { border: 1px solid #dbdbdb; padding: 12px; text-align: left; }
        th { background-color: #34495e; color: white; text-transform: uppercase; font-size: 14px; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h1>Búsqueda de Libros</h1>
    <div class="search-box">
        <form method="get" action="/">
            <input type="text" name="genero" placeholder="Filtrar por género..." value="{{ genero }}">
            <button type="submit">Buscar</button>
        </form>
    </div>
    {% if books %}
    <table>
        <thead>
            <tr>
                {% for col in columns %}
                <th>{{ col }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in books %}
            <tr>
                {% for val in row %}
                <td>{{ val }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p>No se encontraron libros en el catálogo.</p>
    {% endif %}
</body>
</html>
"""

def init_db():
    # Intentar crear la base de datos si no existe conectándose a la base de datos por defecto 'postgres'
    try:
        conn = psycopg2.connect(host='127.0.0.1', port=5432, user='postgres', password='postgres', dbname='postgres')
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test_db';")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE test_db;")
        cur.close()
        conn.close()
    except Exception:
        pass

    # Conectarse a 'test_db' para crear la tabla e insertar datos iniciales
    try:
        conn = psycopg2.connect(host='127.0.0.1', port=5432, user='postgres', password='postgres', dbname='test_db')
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS libros (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL,
                genero VARCHAR(100) NOT NULL,
                autor VARCHAR(255) NOT NULL
            );
        """)
        cur.execute("SELECT COUNT(*) FROM libros;")
        if cur.fetchone()[0] == 0:
            datos_prueba = [
                ('Cien años de soledad', 'Realismo mágico', 'Gabriel García Márquez'),
                ('Don Quijote de la Mancha', 'Novela', 'Miguel de Cervantes'),
                ('Ficciones', 'Fantasía', 'Jorge Luis Borges'),
                ('1984', 'Distopía', 'George Orwell'),
                ('El Aleph', 'Fantasía', 'Jorge Luis Borges')
            ]
            cur.executemany("INSERT INTO libros (titulo, genero, autor) VALUES (%s, %s, %s);", datos_prueba)
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

@app.route('/', methods=['GET'])
def index():
    genero = request.args.get('genero', '').strip()
    try:
        conn = psycopg2.connect(host='127.0.0.1', port=5432, user='postgres', password='postgres', dbname='test_db')
        cur = conn.cursor()
        
        if genero:
            cur.execute("SELECT id, titulo, genero, autor FROM libros WHERE genero ILIKE %s;", (f"%{genero}%",))
        else:
            cur.execute("SELECT id, titulo, genero, autor FROM libros;")
            
        books = cur.fetchall()
        columns = [desc[0].upper() for desc in cur.description]
        cur.close()
        conn.close()
    except Exception:
        return "Ocurrió un problema al consultar el catálogo", 500

    return render_template_string(HTML_TEMPLATE, books=books, columns=columns, genero=genero)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)