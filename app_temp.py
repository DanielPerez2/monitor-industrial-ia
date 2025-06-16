import random
import time
import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# CONFIGURA TU BOT DE TELEGRAM
BOT_TOKEN = '7590291986:AAGhvZDHNS7FmwQHLVyX--Z6oknDXLew7-o'
CHAT_ID = '5870809543'  # ← Reemplázalo por tu chat_id real

# FUNCIONES DE TELEGRAM
def enviar_alerta_telegram(mensaje):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': mensaje}
    requests.post(url, data=data)

# SIMULADORES
def leer_temperatura():
    return random.uniform(20, 80)

def leer_vibracion():
    return random.choice([0, 0, 0, 1])

# CONFIGURACIÓN
UMBRAL_TEMPERATURA = 50
UMBRAL_VIBRACION = 1
historial = []

# CONFIGURA PLOTEO INTERACTIVO
plt.ion()
fig, ax = plt.subplots(figsize=(10, 4))
linea_temp, = ax.plot([], [], marker='o', label='Temperatura')
ax.axhline(y=UMBRAL_TEMPERATURA, color='red', linestyle='--', label='Umbral')
ax.set_ylabel("Temperatura (ºC)")
ax.set_title("Temperatura en tiempo real")
ax.legend()
plt.tight_layout()

print("🟢 Monitor de temperatura iniciado...")

for i in range(20):
    timestamp = datetime.now().strftime("%H:%M:%S")
    temp = leer_temperatura()
    vibra = leer_vibracion()

    historial.append({'hora': timestamp, 'temperatura': temp, 'vibracion': vibra})

    print(f"[{timestamp}] Temp: {temp:.2f} ºC | Vibración: {'ALTA' if vibra else 'OK'}")

    # ALERTAS
    if temp > UMBRAL_TEMPERATURA or vibra == UMBRAL_VIBRACION:
        mensaje = f"🚨 ALERTA [{timestamp}]\n"
        if temp > UMBRAL_TEMPERATURA:
            mensaje += f"Temperatura: {temp:.2f} ºC\n"
        if vibra == UMBRAL_VIBRACION:
            mensaje += f"Vibración fuerte detectada."
        enviar_alerta_telegram(mensaje)

    # ACTUALIZAR GRÁFICO EN TIEMPO REAL
    df = pd.DataFrame(historial)
    linea_temp.set_data(df['hora'], df['temperatura'])
    ax.set_xlim(max(0, len(df) - 10), len(df))
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df['hora'], rotation=45)
    ax.set_ylim(10, 90)
    fig.canvas.draw()
    fig.canvas.flush_events()

    time.sleep(2)

# GUARDAR HISTORIAL
df.to_csv('historial_datos.csv', index=False)
print("🟡 Simulación completada. Historial guardado.")
