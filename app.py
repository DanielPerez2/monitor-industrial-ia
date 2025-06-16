
# ✅ CONFIGURACIÓN INICIAL
import streamlit as st
st.set_page_config(page_title="Monitor Industrial IA", layout="wide")

# --- IMPORTS ---
import pandas as pd
import numpy as np
import joblib
import requests
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

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

# --- FUNCIONES AUXILIARES ---
def leer_datos():
    temperatura = np.random.normal(loc=50, scale=10)
    vibracion = np.random.rand() > 0.8
    hora = datetime.now().strftime("%H:%M:%S")
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

# --- CONECTAR CON GOOGLE SHEETS ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("apt-tracker-463114-h7-83eb18660572.json", scope)
client = gspread.authorize(creds)
sheet = client.open("monitor_ia_datos").sheet1

# --- REVISAR ENCABEZADOS ---
encabezado = sheet.row_values(1)
if encabezado != ["hora", "temperatura", "vibracion"]:
    sheet.update("A1:C1", [["hora", "temperatura", "vibracion"]])

# --- CARGAR MODELO IA ---
try:
    modelo = joblib.load("modelo_ia.joblib")
    ia_disponible = True
except:
    ia_disponible = False

# --- PANEL LATERAL ---
st.sidebar.title("⚙️ Configuración del sistema")
UMBRAL_TEMPERATURA = st.sidebar.slider("Umbral de temperatura (°C)", 30, 90, 50)
alertas_activadas = st.sidebar.toggle("🔔 Activar alertas por Telegram", value=True)
st.sidebar.markdown("---")
st.sidebar.markdown("Versión conectada a Google Sheets ✅")

# --- TÍTULO PRINCIPAL ---
st.title("Monitor Industrial IA")
st.markdown("Sistema de monitoreo con IA, Google Sheets y alertas automáticas.")

# --- LEER DATO ACTUAL Y GUARDAR EN SHEETS ---
dato = leer_datos()
try:
    index = len(sheet.get_all_values()) + 1
    sheet.append_row([dato["hora"], dato["temperatura"], str(dato["vibracion"])], value_input_option='USER_ENTERED')
    st.success(f"📤 Dato guardado en la fila {index} de Google Sheets")
except Exception as e:
    st.error("❌ Error al guardar en Google Sheets:")
    st.code(str(e), language="python")

# --- CARGAR HISTORIAL DESDE SHEETS ---
datos = sheet.get_all_records()
historial = pd.DataFrame(datos)

# --- MOSTRAR ESTADO DEL SISTEMA ---
st.subheader("🔍 Evaluación del sistema IA")
if ia_disponible:
    entrada = [[dato["temperatura"], dato["vibracion"]]]
    pred = modelo.predict(entrada)
    if pred[0] == -1:
        st.markdown("### 🚨 Estado del sistema: **ANOMALÍA DETECTADA**")
        st.error("El sistema ha detectado una anomalía.")
        mensaje = (
            f"⚠️ *Anomalía detectada por IA*\n"
            f"🕒 Hora: {dato['hora']}\n"
            f"🌡️ Temperatura: {dato['temperatura']:.2f} ºC\n"
            f"💥 Vibración: {'Alta' if dato['vibracion'] else 'Normal'}"
        )
        if alertas_activadas:
            enviar_alerta_telegram(mensaje)
    else:
        st.markdown("### ✅ Estado del sistema: **Normal**")
        st.success("Todo funciona dentro de los parámetros esperados.")
else:
    st.info("ℹ️ No se pudo cargar el modelo de IA.")
st.divider()

# --- MOSTRAR GRÁFICO ---
modo_oscuro = st.get_option("theme.base") == "dark"
plt.style.use("dark_background" if modo_oscuro else "default")

st.subheader("📊 Temperatura registrada")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(historial['hora'], historial['temperatura'], marker='o', linewidth=2, color='tab:blue')
ax.axhline(UMBRAL_TEMPERATURA, color='red', linestyle='--', label='Umbral crítico')
ax.set_xlabel("Hora")
ax.set_ylabel("Temperatura (°C)")
ax.legend()
st.pyplot(fig)

# --- HISTORIAL FILTRABLE ---
st.subheader("📂 Historial de registros")

try:
    historial['hora_dt'] = pd.to_datetime(historial['hora'], format="%H:%M:%S").dt.time
except:
    historial['hora_dt'] = historial['hora']

hora_inicio = st.time_input("Hora inicio", value=pd.to_datetime("00:00:00").time())
hora_fin = st.time_input("Hora fin", value=pd.to_datetime("23:59:59").time())

historial_filtrado = historial[
    historial['hora_dt'].apply(lambda h: hora_inicio <= h <= hora_fin)
]

st.dataframe(historial_filtrado[['hora', 'temperatura', 'vibracion']], use_container_width=True)

csv = historial_filtrado[['hora', 'temperatura', 'vibracion']].to_csv(index=False).encode("utf-8")
st.download_button("📥 Descargar historial filtrado (.csv)", data=csv, file_name="historial_filtrado.csv", mime="text/csv")
