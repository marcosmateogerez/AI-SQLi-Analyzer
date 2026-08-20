import psycopg2
from flask import Flask, request, render_template_string

app = Flask(__name__)

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "user": "postgres",
    "password": "postgres",
    "database": "test_db"
}

def init_db():
    # Intentar crear la base de datos 'test_db' si no existe conectándose a 'postgres'
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
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test_db';")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE DATABASE test_db;")
        cur.close()
        conn.close()
    except Exception:
        # Si falla, asumimos que ya existe o se manejará en el siguiente paso
        pass

    # Crear la tabla e insertar datos de prueba
    try:
        conn = psycopg2.connect(**DB_CONFIG)
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
                ('Cien años de soledad', 'Ficción', 'Gabriel García Márquez'),
                ('Don Quijote de la Mancha', 'Clásico', 'Miguel de Cervantes'),
                ('1984', 'Ciencia Ficción', 'George Orwell'),
                ('Ficciones', 'Ficción', 'Jorge Luis Borges'),
                ('Fundación', 'Ciencia Ficción', 'Isaac Asimov')
            ]
            cur.executemany(
                "INSERT INTO libros (titulo, genero, autor) VALUES (%s, %s, %s);",
                datos_prueba
            )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

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
        table { border-collapse: collapse; width: 100%; background-color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        th, td { border: 1px solid #dddddd; text-align: left; padding: 12px; }
        th { background-color: #007BFF; color: white; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .error-msg { color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .no-results { margin-top: 15px; color: #666; }
    </style>
</head>
<body>
    <h1>Buscador de la Biblioteca Digital</h1>
    
    <form method="GET" action="/">
        <input type="text" name="genero" placeholder="Buscar por género (ej. Ficción, Clásico)..." value="{{ genero_buscado }}">
        <button type="submit">Buscar</button>
        <a href="/" style="margin-left: 10px; text-decoration: none; color: #666;">Limpiar filtro</a>
    </form>

    {% if error %}
        <div class="error-msg">
            {{ error }}
        </div>
    {% else %}
        {% if libros %}
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
        {% else %}
            <p class="no-results">No se encontraron libros para el género especificado.</p>
        {% endif %}
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    genero = request.args.get('genero', '').strip()
    libros = []
    error = None
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        if genero:
            sql_query = "SELECT id, titulo, genero, autor FROM libros WHERE genero = %s"
            cur.execute(sql_query, (genero,))
        else:
            sql_query = "SELECT id, titulo, genero, autor FROM libros"
            cur.execute(sql_query)
        libros = cur.fetchall()
        cur.close()
    except Exception:
        error = "Ocurrió un problema al consultar el catálogo"
    finally:
        if conn:
            conn.close()

    return render_template_string(HTML_TEMPLATE, libros=libros, genero_buscado=genero, error=error)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)