from flask import Flask, request, render_template_string
import psycopg2

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
    # Conectar primero a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        dbname="postgres"
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'test_db'")
    exists = cur.fetchone()
    if not exists:
        cur.execute("CREATE DATABASE test_db")
    cur.close()
    conn.close()

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            genero VARCHAR(100) NOT NULL,
            autor VARCHAR(255) NOT NULL
        )
    """)
    conn.commit()

    # Insertar datos de prueba si la tabla está vacía
    cur.execute("SELECT COUNT(*) FROM libros")
    if cur.fetchone()[0] == 0:
        datos_prueba = [
            ('Don Quijote de la Mancha', 'Novela', 'Miguel de Cervantes'),
            ('Cien años de soledad', 'Realismo mágico', 'Gabriel García Márquez'),
            ('1984', 'Distopía', 'George Orwell'),
            ('Ficciones', 'Fantasía', 'Jorge Luis Borges'),
            ('El resplandor', 'Terror', 'Stephen King')
        ]
        cur.executemany("INSERT INTO libros (titulo, genero, autor) VALUES (%s, %s, %s)", datos_prueba)
        conn.commit()
    
    cur.close()
    conn.close()

@app.route('/')
def index():
    genero = request.args.get('genero', '').strip()
    libros = []
    error_message = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if genero:
            cur.execute(
                "SELECT id, titulo, genero, autor FROM libros WHERE genero ILIKE %s", 
                (f"%{genero}%",)
            )
        else:
            cur.execute("SELECT id, titulo, genero, autor FROM libros")
        libros = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        error_message = "Ocurrió un problema al consultar el catálogo"

    html_template = """
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
            tr:nth-child(even) { background-color: #f2f2f2; }
            .error { color: #D8000C; background-color: #FFBABA; padding: 10px; border-radius: 4px; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <h1>Buscador de Libros</h1>
        
        <form method="GET" action="/">
            <input type="text" name="genero" placeholder="Buscar por género (ej. Novela, Terror)..." value="{{ genero }}">
            <button type="submit">Buscar</button>
        </form>

        {% if error_message %}
            <div class="error">{{ error_message }}</div>
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
                    {% else %}
                    <tr>
                        <td colspan="4" style="text-align: center;">No se encontraron libros en esta categoría.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html_template, libros=libros, genero=genero, error_message=error_message)

if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
    app.run(host='127.0.0.1', port=5000, debug=False)