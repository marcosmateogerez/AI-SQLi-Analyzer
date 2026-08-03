import psycopg2
from flask import Flask, request, render_template_string

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres",
            database="postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test_db'")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE DATABASE test_db")
        cur.close()
        conn.close()
    except Exception:
        pass

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
            titulo VARCHAR(255),
            genero VARCHAR(100),
            autor VARCHAR(255)
        )
    """)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM libros")
    count = cur.fetchone()[0]
    if count == 0:
        test_data = [
            ('Don Quijote de la Mancha', 'Novela', 'Miguel de Cervantes'),
            ('Cien años de soledad', 'Realismo mágico', 'Gabriel García Márquez'),
            ('Ficciones', 'Fantasía', 'Jorge Luis Borges'),
            ('1984', 'Distopía', 'George Orwell'),
            ('El Hobbit', 'Fantasía', 'J.R.R. Tolkien')
        ]
        cur.executemany(
            "INSERT INTO libros (titulo, genero, autor) VALUES (%s, %s, %s)",
            test_data
        )
        conn.commit()
    cur.close()
    conn.close()

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Biblioteca Digital</title>
</head>
<body>
    <h1>Búsqueda de Libros</h1>
    <form method="GET" action="/">
        <label for="genero">Género:</label>
        <input type="text" id="genero" name="genero" value="{{ genero }}">
        <button type="submit">Buscar</button>
    </form>

    {% if error %}
        <p style="color: red;">{{ error }}</p>
    {% endif %}

    {% if libros is not none %}
        <h2>Resultados:</h2>
        <table border="1">
            <thead>
                <tr>
                    {% for col in columns %}
                        <th>{{ col | upper }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in libros %}
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

@app.route('/')
def index():
    genero = request.args.get('genero', '')
    libros = []
    columns = []
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
            sql_query = f"SELECT id, titulo, genero, autor FROM libros WHERE genero = '{genero}'"
        else:
            sql_query = "SELECT id, titulo, genero, autor FROM libros"
            
        cur.execute(sql_query)
        columns = [desc[0] for desc in cur.description] if cur.description else []
        libros = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        error = 'Ocurrió un problema al consultar el catálogo'
        libros = None
        columns = []

    return render_template_string(HTML_TEMPLATE, libros=libros, columns=columns, error=error, genero=genero)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)