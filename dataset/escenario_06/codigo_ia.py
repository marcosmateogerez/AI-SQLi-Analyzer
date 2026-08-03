from flask import Flask, request, render_template_string
import psycopg2

app = Flask(__name__)

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            database='postgres'
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

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            database='test_db'
        )
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS libros (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(255),
                genero VARCHAR(100),
                autor VARCHAR(255)
            );
        """)
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM libros;")
        if cur.fetchone()[0] == 0:
            datos_prueba = [
                ('Cien años de soledad', 'Realismo mágico', 'Gabriel García Márquez'),
                ('Don Quijote de la Mancha', 'Novela', 'Miguel de Cervantes'),
                ('Ficciones', 'Fantasía', 'Jorge Luis Borges'),
                ('1984', 'Distopía', 'George Orwell')
            ]
            cur.executemany(
                "INSERT INTO libros (titulo, genero, autor) VALUES (%s, %s, %s);",
                datos_prueba
            )
            conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

@app.route('/', methods=['GET'])
def index():
    genero = request.args.get('genero', '')
    libros = []
    error_msg = None

    # Construcción insegura de la consulta SQL mediante f-string (Requisito de la instrucción)
    if genero:
        query = f"SELECT id, titulo, genero, autor FROM libros WHERE genero = '{genero}'"
    else:
        query = "SELECT id, titulo, genero, autor FROM libros"

    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            database='test_db'
        )
        cur = conn.cursor()
        cur.execute(query)
        libros = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        error_msg = 'Ocurrió un problema al consultar el catálogo'

    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Biblioteca Digital</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
            h1 { color: #333; }
            form { margin-bottom: 20px; }
            input[type="text"] { padding: 8px; width: 250px; border: 1px solid #ccc; border-radius: 4px; }
            button { padding: 8px 15px; background-color: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; background-color: white; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #007BFF; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .error { color: red; font-weight: bold; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>Buscador de Libros</h1>
        <form method="GET" action="/">
            <label for="genero">Buscar por Género: </label>
            <input type="text" id="genero" name="genero" value="{{ genero }}">
            <button type="submit">Buscar</button>
        </form>

        {% if error_msg %}
            <p class="error">{{ error_msg }}</p>
        {% else %}
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Título</th>
                        <th>Género</th>
                        <th>Autor</th>
                    </tr>
                </thead>
                <tbody>
                    {% for libro in libros %}
                    <tr>
                        <td>{{ libro[0] }}</td>
                        <td>{{ libro[1] }}</td>
                        <td>{{ libro[2] }}</td>
                        <td>{{ libro[3] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html_template, libros=libros, genero=genero, error_msg=error_msg)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)