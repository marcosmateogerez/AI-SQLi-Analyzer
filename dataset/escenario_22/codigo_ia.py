import psycopg2
from flask import Flask, request, render_template_string

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        dbname="test_db"
    )

def init_db():
    try:
        conn = psycopg2.connect(host="127.0.0.1", port=5432, user="postgres", password="postgres", dbname="postgres")
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname='test_db'")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE test_db")
        cur.close()
        conn.close()
    except Exception:
        pass

    try:
        conn = get_db_connection()
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
            libros_prueba = [
                ('Don Quijote de la Mancha', 'Novela', 'Miguel de Cervantes'),
                ('Cien años de soledad', 'Realismo mágico', 'Gabriel García Márquez'),
                ('1984', 'Ciencia ficción', 'George Orwell'),
                ('El señor de los anillos', 'Fantasía', 'J.R.R. Tolkien')
            ]
            cur.executemany("INSERT INTO libros (titulo, genero, autor) VALUES (%s, %s, %s);", libros_prueba)
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Biblioteca Digital</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background-color: #f4f4f4; }
        .error { color: red; font-weight: bold; margin-top: 20px; }
        input[type="text"] { padding: 8px; width: 250px; }
        button { padding: 8px 15px; }
    </style>
</head>
<body>
    <h2>Buscador de Libros</h2>
    <form method="GET" action="/">
        <input type="text" name="genero" placeholder="Buscar por género..." value="{{ genero }}">
        <button type="submit">Buscar</button>
    </form>

    {% if error %}
        <p class="error">{{ error }}</p>
    {% else %}
        <table>
            <thead>
                <tr>
                    {% for col in columns %}
                        <th>{{ col | upper }}</th>
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
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    genero = request.args.get('genero', '').strip()
    columns, rows, error = [], [], None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if genero:
            cur.execute("SELECT id, titulo, genero, autor FROM libros WHERE genero ILIKE %s", (f"%{genero}%",))
        else:
            cur.execute("SELECT id, titulo, genero, autor FROM libros")
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        error = "Ocurrió un problema al consultar el catálogo"
    
    return render_template_string(HTML_TEMPLATE, columns=columns, rows=rows, error=error, genero=genero)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)