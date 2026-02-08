# simulador_esp32.py
import requests
import time
import random

# A donde vamos a enviar los datos (Tu propio servidor local)
URL_SERVIDOR = "http://127.0.0.1:5000/api/guardar"

print(f"--- Iniciando Simulación de Sensor ESP32 hacia {URL_SERVIDOR} ---")

while True:
    # 1. Generar datos aleatorios (Simulamos el sensor)
    bpm_fake = random.randint(55, 110)  # BPM entre 55 y 110
    spo2_fake = random.randint(85, 99)  # SpO2 entre 85% y 99%
    
    # 2. Empaquetar los datos (Payload)
    datos_para_enviar = {
        'bpm': bpm_fake,
        'spo2': spo2_fake
    }
    
    try:
        # 3. ENVIAR petición POST (Esto reemplaza al HTTPClient del ESP32)
        respuesta = requests.post(URL_SERVIDOR, data=datos_para_enviar)
        
        if respuesta.status_code == 200:
            print(f"✅ Enviado: BPM={bpm_fake}, SpO2={spo2_fake}%")
        else:
            print(f"❌ Error del servidor: {respuesta.status_code}")
            
    except Exception as e:
        print(f"⚠️ No se pudo conectar con el servidor. ¿Está corriendo app.py?")
        
    # 4. Esperar un poco antes del siguiente dato
    time.sleep(1) # Envía un dato cada 2 segundos