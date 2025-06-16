import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import random
import joblib
import requests

# CONFIGURACIÓN GENERAL
st.set_page_config(page_title="Monitor Industrial IA", layout="wide")
UMBRAL_TEMPERATURA = 50
UMBRAL_VIBRACION = 1

# TELEGRAM - Sustituye con tu TOKEN y tu CHAT_ID reales
BOT_TOKEN = '7590291986:AAGhvZDHNS7FmwQHLVyX--Z6oknDXLew7-o'
CHAT_ID = '5870809543'  # ← Reemplázalo por tu número

def enviar_alerta_telegram(mensaje):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': mensaje}
    try:
        r = requests.post(url, data=data)
        print(f"Telegram status: {r.status_code}")
    except Exception as e:
        print("❌ Error al enviar alerta:", e)

# SIMULACIÓN DE DATOS
@st.cache_data(ttl=2)
def leer_datos():
    ahora = datetime.now().strftime("%H:%M:%S")
    temperatura = random.uniform(20, 80)  # Cambia aquí a 75 si quieres forzar alerta
    vibracion = random.choice([0, 0, 0, 1])  # 25% probabilidad de vibración fuerte
    return {'hora': ahora, 'temperatura': temperatura, 'vibracion': vibracion}

# HISTORIAL CSV
def cargar_historial():
    try:
        return pd.read_csv('historial_datos.csv')
    except:
        return pd.DataFrame(columns=['hora', 'temperatura', 'vibracion'])

def guardar_dato(df, nuevo):
    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    df.to_csv('historial_datos.csv', index=False)
    return df

# CARGAR MODELO IA
try:
    modelo = joblib.load('modelo_ia.joblib')
    ia_disponible = True
except:
    ia_disponible = False

# CABECERA
st.title("🧠 Monitor Industrial con IA")
st.markdown("Visualización de sensores simulados y detección automática de anomalías con alertas por Telegram.")

# LEER NUEVO DATO
dato = leer_datos()
historial = cargar_historial()
historial = guardar_dato(historial, dato)

# MÉTRICAS
col1, col2 = st.columns(2)
with col1:
    st.metric("🌡️ Temperatura", f"{dato['temperatura']:.2f} ºC")
    st.progress(min(dato['temperatura'] / UMBRAL_TEMPERATURA, 1.0))
with col2:
    st.metric("💥 Vibración", "ALTA" if dato['vibracion'] else "Normal")
    if dato['vibracion']:
        st.warning("⚠️ Vibración fuera de rango")

# PREDICCIÓN IA + ALERTA
st.subheader("🔍 Evaluación del sistema IA")

if ia_disponible:
    entrada = [[dato['temperatura'], dato['vibracion']]]
    pred = modelo.predict(entrada)

    if pred[0] == -1:
        st.error("🚨 ANOMALÍA DETECTADA")
        mensaje = (
            f"⚠️ *Anomalía detectada por IA*\n"
            f"🕒 Hora: {dato['hora']}\n"
            f"🌡️ Temperatura: {dato['temperatura']:.2f} ºC\n"
            f"💥 Vibración: {'Alta' if dato['vibracion'] else 'Normal'}"
        )
        enviar_alerta_telegram(mensaje)
    else:
        st.success("✅ Todo normal según la IA")
else:
    st.info("ℹ️ No se pudo cargar el modelo de IA. Entrénalo con entrenar_ia.py")

# GRÁFICO DE TEMPERATURA
st.subheader("📈 Historial de temperatura")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(historial['hora'], historial['temperatura'], marker='o')
ax.axhline(UMBRAL_TEMPERATURA, color='red', linestyle='--', label='Umbral')
ax.set_xticks(range(len(historial)))
ax.set_xticklabels(historial['hora'], rotation=45)
ax.set_ylabel("Temperatura (ºC)")
ax.set_ylim(10, 90)
ax.legend()
st.pyplot(fig)

# DESCARGA CSV
st.download_button(
    label="📁 Descargar historial CSV",
    data=historial.to_csv(index=False).encode('utf-8'),
    file_name='historial_datos.csv',
    mime='text/csv'
)

