from flask import Flask, request, render_template_string
import sqlite3
from datetime import datetime

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

# --- API: Recibir datos ---
@app.route('/api/guardar', methods=['POST'])
def guardar_datos():
    bpm = request.form.get('bpm')
    spo2 = request.form.get('spo2')
    
    estado = "Normal"
    if bpm and spo2:
        if float(bpm) > 100 or float(spo2) < 90:
            estado = "PELIGRO"

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO signos_vitales (bpm, spo2, estado) VALUES (?, ?, ?)", 
                       (bpm, spo2, estado))
        conn.commit()
        conn.close()
        print(f"📡 DATO: BPM={bpm}, SpO2={spo2}")
        return "Guardado", 200
    return "Error", 400

# --- Frontend: Dashboard Futurista ---
@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Traemos los últimos 50 datos para la tabla
    cursor.execute("SELECT * FROM signos_vitales ORDER BY timestamp DESC LIMIT 50")
    filas = cursor.fetchall()
    
    # 2. Lógica para determinar si está "CONECTADO"
    # Miramos la fecha del último dato recibido
    estado_conexion = "OFFLINE"
    ultimo_dato_hora = "Sin Datos"
    
    if filas:
        ultimo_dato = filas[0] # El más reciente (índice 0)
        ultimo_dato_hora = ultimo_dato['timestamp']
        
        # Convertimos el string de la DB a objeto fecha de Python
        fecha_dato = datetime.strptime(ultimo_dato['timestamp'], '%Y-%m-%d %H:%M:%S')
        ahora = datetime.now()
        
        # Si la diferencia es menor a 15 segundos, asumimos que está conectado
        diferencia = (ahora - fecha_dato).total_seconds()
        if diferencia < 15:
            estado_conexion = "ONLINE"

    conn.close()
    
    # Fecha actual para el header
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    # --- HTML + CSS INCRUSTADO ---
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="5"> 
        <title>ESP32 Health Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        
        <style>
            :root {
                --bg-color: #1e1e1e;       /* Fondo VS Code */
                --panel-bg: #252526;       /* Paneles */
                --accent: #007acc;         /* Azul VS Code */
                --text: #d4d4d4;           /* Texto Gris Claro */
                --border: #3e3e42;         /* Bordes sutiles */
                --success: #4ec9b0;        /* Verde suave */
                --danger: #f44747;         /* Rojo suave */
                --warning: #ce9178;        /* Naranja suave */
            }

            body {
                background-color: var(--bg-color);
                color: var(--text);
                font-family: 'Fira Code', monospace; /* Fuente de programador */
                margin: 0;
                padding: 20px;
                height: 100vh;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                overflow: hidden; /* Evita scroll en toda la página */
            }

            /* --- HEADER (METADATOS) --- */
            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-bottom: 20px;
                border-bottom: 1px solid var(--border);
                margin-bottom: 20px;
            }

            .device-info h1 { margin: 0; font-size: 1.5rem; color: var(--accent); }
            .device-info p { margin: 0; font-size: 0.8rem; color: #858585; }
            
            .meta-tags {
                display: flex;
                gap: 15px;
            }

            .tag {
                background: var(--panel-bg);
                border: 1px solid var(--border);
                padding: 5px 15px;
                border-radius: 4px;
                font-size: 0.9rem;
            }

            .tag i { color: var(--accent); margin-right: 8px; }

            /* --- LAYOUT PRINCIPAL (GRID) --- */
            .main-grid {
                display: grid;
                grid-template-columns: 300px 1fr; /* Panel izq fijo, der flexible */
                gap: 20px;
                height: 100%;
                overflow: hidden;
            }

            /* --- PANELES COMUNES --- */
            .panel {
                background-color: var(--panel-bg);
                border: 1px solid var(--border);
                border-radius: 6px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                display: flex;
                flex-direction: column;
            }

            h2 {
                margin-top: 0;
                font-size: 1.1rem;
                border-bottom: 1px solid var(--border);
                padding-bottom: 10px;
                color: var(--accent);
                display: flex;
                align-items: center;
                gap: 10px;
            }

            /* --- PANEL 1: ESTADO --- */
            .status-card {
                margin-top: 20px;
                text-align: center;
            }

            .status-indicator {
                font-size: 2rem;
                font-weight: bold;
                margin: 10px 0;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }

            .online { color: var(--success); text-shadow: 0 0 10px rgba(78, 201, 176, 0.4); }
            .offline { color: #666; }

            /* Animación de parpadeo */
            .blink { animation: blinker 1.5s linear infinite; }
            @keyframes blinker { 50% { opacity: 0; } }

            .stat-row {
                display: flex;
                justify-content: space-between;
                margin-top: 15px;
                font-size: 0.9rem;
                padding: 10px;
                background: rgba(0,0,0,0.2);
                border-radius: 4px;
            }

            /* --- PANEL 2: TABLA --- */
            .table-container {
                flex-grow: 1;
                overflow-y: auto; /* SCROLL SOLO AQUI */
                margin-top: 10px;
            }

            /* Estilo Scrollbar tipo VS Code */
            .table-container::-webkit-scrollbar { width: 10px; }
            .table-container::-webkit-scrollbar-track { background: var(--bg-color); }
            .table-container::-webkit-scrollbar-thumb { background: #424242; border-radius: 5px; }
            .table-container::-webkit-scrollbar-thumb:hover { background: #4f4f4f; }

            table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.9rem;
            }

            th {
                position: sticky; /* Cabecera fija al bajar */
                top: 0;
                background-color: var(--panel-bg);
                color: var(--accent);
                padding: 10px;
                text-align: left;
                border-bottom: 2px solid var(--accent);
                z-index: 2;
            }

            td {
                padding: 8px 10px;
                border-bottom: 1px solid var(--border);
            }

            tr:hover { background-color: #2d2d30; }

            /* Etiquetas de estado en la tabla */
            .badge {
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 0.8rem;
                font-weight: bold;
            }
            .badge-normal { background: rgba(78, 201, 176, 0.1); color: var(--success); border: 1px solid var(--success); }
            .badge-peligro { background: rgba(244, 71, 71, 0.1); color: var(--danger); border: 1px solid var(--danger); }

        </style>
    </head>
    <body>

        <header>
            <div class="device-info">
                <h1><i class="fas fa-microchip"></i> MONITOR IOT - ESP32</h1>
                <p>ID Dispositivo: XC-4022-LAB | Firmware v1.0.4</p>
            </div>
            
            <div class="meta-tags">
                <div class="tag"><i class="far fa-calendar-alt"></i> {{ fecha_hoy }}</div>
                <div class="tag"><i class="fas fa-network-wired"></i> IP: 192.168.1.XX</div>
                <div class="tag"><i class="fas fa-user-md"></i> Admin: Estudiante UTN</div>
            </div>
        </header>

        <div class="main-grid">
            
            <div class="panel">
                <h2><i class="fas fa-wifi"></i> Estado de Red</h2>
                
                <div class="status-card">
                    <p style="margin:0; color:#858585;">CONECTIVIDAD</p>
                    <div class="status-indicator {{ 'online' if estado_conexion == 'ONLINE' else 'offline' }}">
                        <i class="fas fa-circle {{ 'blink' if estado_conexion == 'ONLINE' else '' }}"></i>
                        {{ estado_conexion }}
                    </div>
                </div>

                <div class="stat-row">
                    <span><i class="fas fa-bolt"></i> Batería</span>
                    <span style="color: var(--success);">98%</span>
                </div>
                <div class="stat-row">
                    <span><i class="fas fa-clock"></i> Último Dato</span>
                    <span>{{ ultimo_dato_hora.split(' ')[1] if ultimo_dato_hora != 'Sin Datos' else '--:--' }}</span>
                </div>
                <div class="stat-row">
                    <span><i class="fas fa-server"></i> Servidor</span>
                    <span style="color: var(--accent);">Activo (Flask)</span>
                </div>
            </div>

            <div class="panel">
                <h2><i class="fas fa-table"></i> Registros en Tiempo Real</h2>
                
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>TIMESTAMP</th>
                                <th>BPM (Pulso)</th>
                                <th>SpO2 (Oxígeno)</th>
                                <th>ESTADO</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for fila in filas %}
                            <tr>
                                <td style="color: #569cd6;">{{ fila['timestamp'] }}</td>
                                <td>
                                    <i class="fas fa-heartbeat" style="color: #f44747;"></i> {{ fila['bpm'] }}
                                </td>
                                <td>{{ fila['spo2'] }}%</td>
                                <td>
                                    <span class="badge {{ 'badge-peligro' if fila['estado'] == 'PELIGRO' else 'badge-normal' }}">
                                        {{ fila['estado'] }}
                                    </span>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

        </div>

    </body>
    </html>
    """
    
    return render_template_string(html, filas=filas, fecha_hoy=fecha_hoy, estado_conexion=estado_conexion, ultimo_dato_hora=ultimo_dato_hora)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)