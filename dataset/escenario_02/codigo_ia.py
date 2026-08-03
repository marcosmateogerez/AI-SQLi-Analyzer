import psycopg2
from flask import Flask, request, render_template_string

app = Flask(__name__)

def get_db_connection(dbname="test_db"):
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        dbname=dbname
    )

def init_db():
    # Crear la base de datos si no existe
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
            datos_prueba = [
                ('Cien años de soledad', 'Realismo mágico', 'Gabriel García Márquez'),
                ('Don Quijote de la Mancha', 'Novela', 'Miguel de Cervantes'),
                ('Ficciones', 'Fantasía', 'Jorge Luis Borges'),
                ('1984', 'Distopía', 'George Orwell'),
                ('El Aleph', 'Fantasía', 'Jorge Luis Borges')
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

@app.route('/')
def index():
    genero = request.args.get('genero', '').strip()
    libros = []
    columnas = []
    error_mensaje = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if genero:
            cur.execute(
                "SELECT id, titulo, genero, autor FROM libros WHERE genero ILIKE %s;",
                (f"%{genero}%",)
            )
        else:
            cur.execute("SELECT id, titulo, genero, autor FROM libros;")
        
        libros = cur.fetchall()
        columnas = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
    except Exception:
        error_mensaje = "Ocurrió un problema al consultar el catálogo"

    template = """
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
            th { background-color: #007BFF; color: white; text-transform: uppercase; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .error { color: #D8000C; background-color: #FFBABA; padding: 10px; border-radius: 4px; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <h1>Buscador de Libros</h1>
        
        <form method="GET" action="/">
            <input type="text" name="genero" placeholder="Buscar por género (ej. Fantasía)" value="{{ genero }}">
            <button type="submit">Buscar</button>
        </form>

        {% if error_mensaje %}
            <div class="error">{{ error_mensaje }}</div>
        {% else %}
            <table>
                <thead>
                    <tr>
                        {% for col in columnas %}
                            <th>{{ col }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for libro in libros %}
                        <tr>
                            {% for campo in libro %}
                                <td>{{ campo }}</td>
                            {% endfor %}
                        </tr>
                    {% else %}
                        <tr>
                            <td colspan="{{ columnas|length if columnas else 1 }}">No se encontraron resultados.</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(
        template, 
        libros=libros, 
        columnas=columnas, 
        genero=genero, 
        error_mensaje=error_mensaje
    )

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)