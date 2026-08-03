import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Biblioteca Digital - Buscador</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
        h1 { color: #333; }
        form { margin-bottom: 20px; }
        input[type="text"] { padding: 8px; width: 250px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 8px 15px; background-color: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        th, td { border: 1px solid #dddddd; text-align: left; padding: 12px; }
        th { background-color: #007BFF; color: white; text-transform: uppercase; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .error { color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 4px; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Buscador de Libros</h1>
    <form method="GET" action="/">
        <label for="genero">Buscar por Género: </label>
        <input type="text" id="genero" name="genero" value="{{ genero }}" placeholder="Ej. Ficción, Ciencia Ficción...">
        <button type="submit">Buscar</button>
    </form>

    {% if error %}
        <div class="error">
            {{ error }}
        </div>
    {% else %}
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
                        {% for cell in row %}
                            <td>{{ cell }}</td>
                        {% endfor %}
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    {% endif %}
</body>
</html>
"""

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test_db'")
    exists = cur.fetchone()
    if not exists:
        cur.execute("CREATE DATABASE test_db")
    
    cur.close()
    conn.close()

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        database="test_db"
    )
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            genero VARCHAR(100) NOT NULL,
            autor VARCHAR(255) NOT NULL
        )
    """)
    
    cur.execute("SELECT COUNT(*) FROM libros")
    count = cur.fetchone()[0]
    
    if count == 0:
        datos_prueba = [
            ('Cien años de soledad', 'Ficción', 'Gabriel García Márquez'),
            ('Don Quijote de la Mancha', 'Clásico', 'Miguel de Cervantes'),
            ('1984', 'Ciencia Ficción', 'George Orwell'),
            ('Ficciones', 'Ficción', 'Jorge Luis Borges'),
            ('Fundación', 'Ciencia Ficción', 'Isaac Asimov')
        ]
        cur.executemany(
            "INSERT INTO libros (titulo, genero, autor) VALUES (%s, %s, %s)",
            datos_prueba
        )
        conn.commit()
        
    cur.close()
    conn.close()

@app.route('/', methods=['GET'])
def index():
    genero = request.args.get('genero', '').strip()
    rows = []
    colnames = []
    error = None

    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres",
            database="test_db"
        )
        cur = conn.cursor()

        if genero:
            sql_query = "SELECT id, titulo, genero, autor FROM libros WHERE genero = %s"
            cur.execute(sql_query, (genero,))
        else:
            sql_query = "SELECT id, titulo, genero, autor FROM libros"
            cur.execute(sql_query)

        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        
        cur.close()
        conn.close()
    except Exception:
        error = "Ocurrió un problema al consultar el catálogo"

    return render_template_string(
        HTML_TEMPLATE,
        rows=rows,
        colnames=colnames,
        genero=genero,
        error=error
    )

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)