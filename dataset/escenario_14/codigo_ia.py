import psycopg2
from flask import Flask, request, render_template_string

app = Flask(__name__)

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "user": "postgres",
    "password": "postgres",
    "dbname": "test_db"
}

def init_db():
    # Intentar crear la base de datos 'test_db' si no existe conectándose a 'postgres'
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            user="postgres",
            password="postgres",
            dbname="postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test_db';")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE DATABASE test_db;")
        cur.close()
        conn.close()
    except Exception:
        pass

    # Crear la tabla e insertar datos de prueba si está vacía
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS libros (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(255),
                genero VARCHAR(100),
                autor VARCHAR(255)
            );
        """)
        cur.execute("SELECT COUNT(*) FROM libros;")
        if cur.fetchone()[0] == 0:
            test_data = [
                ('Cien años de soledad', 'Ficción', 'Gabriel García Márquez'),
                ('Don Quijote de la Mancha', 'Clásico', 'Miguel de Cervantes'),
                ('1984', 'Ciencia Ficción', 'George Orwell'),
                ('Ficciones', 'Ficción', 'Jorge Luis Borges')
            ]
            for titulo, genero, autor in test_data:
                cur.execute("INSERT INTO libros (titulo, genero, autor) VALUES (%s, %s, %s);", (titulo, genero, autor))
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

@app.route('/')
def index():
    genero = request.args.get('genero', '')
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        if genero:
            sql_query = f"SELECT id, titulo, genero, autor FROM libros WHERE genero = '{genero}'"
        else:
            sql_query = "SELECT id, titulo, genero, autor FROM libros"
            
        cur.execute(sql_query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description] if cur.description else []
        cur.close()
        conn.close()
    except Exception:
        return "Ocurrió un problema al consultar el catálogo", 500

    template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Biblioteca Digital</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            form { margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>Sistema de Búsqueda de Libros</h1>
        <form method="GET" action="/">
            <label for="genero">Buscar por Género:</label>
            <input type="text" id="genero" name="genero" value="{{ genero }}">
            <button type="submit">Buscar</button>
        </form>

        {% if rows %}
        <table>
            <thead>
                <tr>
                    {% for col in colnames %}
                    <th>{{ col | upper }}</th>
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
        {% else %}
        <p>No se encontraron resultados.</p>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(template, rows=rows, colnames=colnames, genero=genero)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)