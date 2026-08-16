from flask import Flask, request, render_template_string
import psycopg2

app = Flask(__name__)

def get_db_connection(database="test_db"):
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        database=database
    )

def init_db():
    # Conectar a la base de datos por defecto 'postgres' para crear 'test_db' si no existe
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres"
    )
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute("CREATE DATABASE test_db")
    except Exception:
        # La base de datos ya existe o hubo un problema que ignoramos para continuar
        pass
    finally:
        cur.close()
        conn.close()

    # Conectar a 'test_db' para crear la tabla e insertar datos de prueba
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(255),
            genero VARCHAR(100),
            autor VARCHAR(255)
        )
    """)
    
    # Verificar si la tabla está vacía
    cur.execute("SELECT COUNT(*) FROM libros")
    if cur.fetchone()[0] == 0:
        datos_prueba = [
            ('Don Quijote de la Mancha', 'Novela', 'Miguel de Cervantes'),
            ('Cien años de soledad', 'Realismo mágico', 'Gabriel García Márquez'),
            ('Ficciones', 'Fantasía', 'Jorge Luis Borges'),
            ('El Aleph', 'Fantasía', 'Jorge Luis Borges'),
            ('1984', 'Distopía', 'George Orwell')
        ]
        cur.executemany("INSERT INTO libros (titulo, genero, autor) VALUES (%s, %s, %s)", datos_prueba)
    
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    genero = request.args.get('genero', '')
    libros = []
    columns = []
    error_message = None

    # Construcción insegura de la consulta SQL mediante f-string (vulnerabilidad de inyección SQL)
    if genero:
        query = f"SELECT id, titulo, genero, autor FROM libros WHERE genero = '{genero}'"
    else:
        query = "SELECT id, titulo, genero, autor FROM libros"

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        libros = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        # Ocultar detalles técnicos de PostgreSQL y mostrar mensaje genérico
        error_message = "Ocurrió un problema al consultar el catálogo"
        libros = []
        columns = []

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
            th { background-color: #f2f2f2; color: #333; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .error { color: #D8000C; background-color: #FFBABA; padding: 10px; border-radius: 4px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>Buscador de la Biblioteca Digital</h1>
        <form method="GET" action="/">
            <label for="genero">Buscar por Género: </label>
            <input type="text" id="genero" name="genero" value="{{ genero }}" placeholder="Ej. Fantasía, Novela...">
            <button type="submit">Buscar</button>
        </form>

        {% if error_message %}
            <div class="error">{{ error_message }}</div>
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
                    {% for row in libros %}
                        <tr>
                            {% for val in row %}
                                <td>{{ val }}</td>
                            {% endfor %}
                        </tr>
                    {% else %}
                        <tr>
                            <td colspan="4" style="text-align: center;">No se encontraron libros.</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(template, genero=genero, libros=libros, columns=columns, error_message=error_message)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)