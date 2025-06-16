
# ✅ CONFIGURACIÓN INICIAL
import streamlit as st
st.set_page_config(page_title="Monitor Industrial IA", layout="wide")

# --- IMPORTS ---
import pandas as pd
import numpy as np
import joblib
import requests
import matplotlib.pyplot as plt
import os
import json
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- LOGIN BÁSICO ---
if 'login_exitoso' not in st.session_state:
    st.session_state.login_exitoso = False

if not st.session_state.login_exitoso:
    st.title("🔐 Acceso al sistema")
    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if user == "daniel" and password == "demo123":
            st.session_state.login_exitoso = True
        else:
            st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()

# --- CONEXIÓN A GOOGLE SHEETS ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
cred_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("monitor_ia_datos").sheet1

# --- FUNCIONES ---
def leer_datos():
    temperatura = np.random.normal(loc=50, scale=10)
    vibracion = np.random.rand() > 0.8
    hora = pd.Timestamp.now().strftime("%H:%M:%S")
    return {"hora": hora, "temperatura": temperatura, "vibracion": vibracion}

def enviar_alerta_telegram(mensaje):
    token = "7590291986:AAGhvZDHNS7FmwQHLVyX--Z6oknDXLew7-o"
    chat_id = "5870809543"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except:
        pass

# --- CARGAR MODELO IA ---
try:
    modelo = joblib.load("modelo_ia.joblib")
    ia_disponible = True
except:
    ia_disponible = False

# --- PANEL DE CONFIGURACIÓN ---
st.sidebar.title("⚙️ Configuración del sistema")
UMBRAL_TEMPERATURA = st.sidebar.slider("Umbral de temperatura (°C)", 30, 90, 50)
alertas_activadas = st.sidebar.toggle("🔔 Activar alertas por Telegram", value=True)
st.sidebar.markdown("---")
st.sidebar.markdown("Versión demo por Daniel Pérez")

# --- LECTURA DE DATO SIMULADO ---
dato = leer_datos()

# --- ESTADO GENERAL DEL SISTEMA ---
st.title("Monitor Industrial IA")
st.markdown("Visualización en tiempo real de sensores industriales con IA y alertas automáticas.")

if ia_disponible:
    entrada = [[dato['temperatura'], dato['vibracion']]]
    pred = modelo.predict(entrada)
    if pred[0] == -1:
        st.markdown("### 🚨 Estado del sistema: **ANOMALÍA DETECTADA**")
        st.error("El sistema ha detectado una anomalía.")
    else:
        st.markdown("### ✅ Estado del sistema: **Normal**")
        st.success("Todo funciona dentro de lo esperado.")
else:
    st.info("ℹ️ No se pudo cargar el modelo de IA.")

st.divider()

# --- GUARDAR EN GOOGLE SHEETS ---
sheet.append_row([dato["hora"], dato["temperatura"], str(dato["vibracion"])], value_input_option="USER_ENTERED")

# --- HISTORIAL LOCAL PARA GRÁFICO ---
historial_path = "historial_datos.csv"
if os.path.exists(historial_path):
    historial = pd.read_csv(historial_path)
else:
    historial = pd.DataFrame(columns=["hora", "temperatura", "vibracion"])

nuevo = pd.DataFrame([dato])
historial = pd.concat([historial, nuevo], ignore_index=True)
historial.to_csv(historial_path, index=False)

# --- GRÁFICO DE TEMPERATURA ---
st.subheader("📊 Temperatura registrada")
modo_oscuro = st.get_option("theme.base") == "dark"
plt.style.use("dark_background" if modo_oscuro else "default")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(historial['hora'], historial['temperatura'], marker='o', linewidth=2, markersize=6, color='tab:blue')
ax.axhline(UMBRAL_TEMPERATURA, color='red', linestyle='--', label='Umbral crítico')
ax.set_xlabel("Hora")
ax.set_ylabel("Temperatura (°C)")
ax.legend()
plt.xticks(rotation=45)
st.pyplot(fig)

# --- EVALUACIÓN IA + ALERTAS ---
st.subheader("🔍 Evaluación del sistema IA")
if ia_disponible:
    if pred[0] == -1:
        mensaje = f"⚠️ *Anomalía detectada*\n🕒 {dato['hora']} | 🌡️ {dato['temperatura']:.2f} ºC | 💥 Vibración: {'Alta' if dato['vibracion'] else 'Normal'}"
        if alertas_activadas:
            enviar_alerta_telegram(mensaje)
        st.error("🚨 Anomalía detectada por IA")
    else:
        st.success("✅ Estado normal según IA")
else:
    st.info("ℹ️ No se pudo cargar el modelo de IA.")

# --- HISTORIAL FILTRABLE ---
st.subheader("📂 Historial de registros")
try:
    historial['hora_dt'] = pd.to_datetime(historial['hora'], format="%H:%M:%S").dt.time
except:
    historial['hora_dt'] = historial['hora']

hora_inicio = st.time_input("Hora inicio", pd.to_datetime("00:00:00").time())
hora_fin = st.time_input("Hora fin", pd.to_datetime("23:59:59").time())
historial_filtrado = historial[historial['hora_dt'].apply(lambda h: hora_inicio <= h <= hora_fin)]
st.dataframe(historial_filtrado[['hora', 'temperatura', 'vibracion']], use_container_width=True)
csv = historial_filtrado[['hora', 'temperatura', 'vibracion']].to_csv(index=False).encode("utf-8")
st.download_button("📥 Descargar historial filtrado (.csv)", data=csv, file_name="historial_filtrado.csv", mime="text/csv")
