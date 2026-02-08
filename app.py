# app.py
from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)
DB_NAME = "healthcare.db"

# --- Inicializar DB ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signos_vitales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            bpm REAL,
            spo2 REAL,
            estado TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- Endpoint API (El que recibe los datos) ---
@app.route('/api/guardar', methods=['POST'])
def guardar_datos():
    bpm = request.form.get('bpm')
    spo2 = request.form.get('spo2')
    
    # Lógica de Alerta simple
    estado = "Normal"
    if float(bpm) > 100 or float(spo2) < 90:
        estado = "PELIGRO"

    if bpm and spo2:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO signos_vitales (bpm, spo2, estado) VALUES (?, ?, ?)", 
                       (bpm, spo2, estado))
        conn.commit()
        conn.close()
        print(f"📡 DATO RECIBIDO: BPM={bpm}, SpO2={spo2}") # Log en consola
        return "Guardado", 200
    return "Error", 400

# --- Página Web (Frontend) ---
@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM signos_vitales ORDER BY timestamp DESC LIMIT 15")
    filas = cursor.fetchall()
    conn.close()

    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="2"> <title>Monitor IoT</title>
        <style>
            body { font-family: sans-serif; background: #222; color: #eee; text-align: center; }
            table { margin: 20px auto; border-collapse: collapse; width: 80%; }
            th, td { border: 1px solid #555; padding: 10px; }
            th { background: #444; color: #00aaff; }
            .alerta { background: #aa0000; color: white; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Monitor Cardíaco IoT</h1>
        <table>
            <tr><th>Hora</th><th>BPM</th><th>SpO2</th><th>Estado</th></tr>
            {% for fila in filas %}
            <tr class="{{ 'alerta' if fila['estado'] == 'PELIGRO' else '' }}">
                <td>{{ fila['timestamp'] }}</td>
                <td>{{ fila['bpm'] }}</td>
                <td>{{ fila['spo2'] }}%</td>
                <td>{{ fila['estado'] }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html, filas=filas)

if __name__ == '__main__':
    init_db()
    # Ejecutamos en puerto 5000
    app.run(host='0.0.0.0', port=5000, debug=True)