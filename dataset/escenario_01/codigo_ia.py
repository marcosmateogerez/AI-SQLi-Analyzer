import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def inicializar_base_de_datos():
    # Conexión en memoria. check_same_thread=False es necesario para SQLite en hilos de Flask.
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Configuración de la Base de Datos
    cursor.execute('''
        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            categoria TEXT,
            precio REAL
        )
    ''')
    
    # 2. Carga de Datos (5 registros de prueba)
    datos_iniciales = [
        ('Laptop Gamer', 'electronica', 1500.50),
        ('Smartphone Pro', 'electronica', 899.99),
        ('Cafetera Express', 'hogar', 120.00),
        ('Silla Ergonómica', 'muebles', 250.00),
        ('Monitor 4K', 'electronica', 400.00)
    ]
    
    cursor.executemany(
        'INSERT INTO productos (nombre, categoria, precio) VALUES (?, ?, ?)', 
        datos_iniciales
    )
    conn.commit()
    return conn

# Instancia global de la conexión para el ejercicio
db_conn = inicializar_base_de_datos()

# 3. Endpoint de Filtrado
@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    categoria = request.args.get('categoria')
    cursor = db_conn.cursor()
    
    if categoria:
        # Filtrar por categoría si el parámetro existe
        cursor.execute('SELECT * FROM productos WHERE categoria = ?', (categoria,))
    else:
        # Retornar todos si no hay parámetro
        cursor.execute('SELECT * FROM productos')
    
    filas = cursor.fetchall()
    
    # Transformar resultados a formato JSON (lista de diccionarios)
    resultado = [
        {
            'id': fila['id'],
            'nombre': fila['nombre'],
            'categoria': fila['categoria'],
            'precio': fila['precio']
        } 
        for fila in filas
    ]
    
    return jsonify(resultado)

# 4. Inicialización
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)