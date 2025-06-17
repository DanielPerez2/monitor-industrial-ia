
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests
import os
import matplotlib.pyplot as plt

# Configuración de página
st.set_page_config(page_title="Monitor Industrial IA", layout="wide")

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

# --- FUNCIONES ---
def leer_datos():
    temperatura = np.random.normal(loc=50, scale=10)
    vibracion = np.random.rand() > 0.8
    import pytz
    hora = pd.Timestamp.now(tz=pytz.timezone("Europe/Madrid")).strftime("%H:%M:%S")

    return {"temperatura": temperatura, "vibracion": vibracion, "hora": hora}

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
UMBRAL_TEMPERATURA = st.sidebar.slider("Umbral de temperatura (°C)", min_value=30, max_value=90, value=50)
alertas_activadas = st.sidebar.toggle("🔔 Activar alertas por Telegram", value=True)
st.sidebar.markdown("---")
st.sidebar.markdown("Versión demo por Daniel Pérez")

# --- INICIO APP ---
st.title("Monitor Industrial IA")
st.markdown("Visualización de sensores simulados y detección automática de anomalías con alertas por Telegram.")

# --- LEER DATO ACTUAL ---
dato = leer_datos()
# --- MOSTRAR DATOS ACTUALES ---
col1, col2 = st.columns(2)
with col1:
    st.metric("🌡️ Temperatura actual", f"{dato['temperatura']:.2f} ºC")
with col2:
    vibracion_texto = "Alta" if dato["vibracion"] else "Normal"
    st.metric("💥 Vibración", vibracion_texto)


# --- ESTADO GENERAL ---
if ia_disponible:
    entrada = [[dato['temperatura'], dato['vibracion']]]
    pred = modelo.predict(entrada)
    if pred[0] == -1:
        st.markdown("### 🚨 Estado del sistema: **ANOMALÍA DETECTADA**")
        st.error("El sistema ha detectado una anomalía en los sensores.")
    else:
        st.markdown("### ✅ Estado del sistema: **Normal**")
        st.success("Todo funciona dentro de los parámetros esperados.")
else:
    st.info("ℹ️ No se pudo cargar el modelo de IA.")
st.divider()

# --- GUARDAR EN HISTORIAL ---
historial_path = "historial_datos.csv"
if os.path.exists(historial_path):
    historial = pd.read_csv(historial_path)
else:
    historial = pd.DataFrame(columns=["hora", "temperatura", "vibracion"])

nuevo = pd.DataFrame([dato])
historial = pd.concat([historial, nuevo], ignore_index=True)
historial.to_csv(historial_path, index=False)

# --- MOSTRAR GRÁFICO ---
modo_oscuro = st.get_option("theme.base") == "dark"
plt.style.use("dark_background" if modo_oscuro else "default")

st.subheader("📊 Temperatura registrada")
fig, ax = plt.subplots(figsize=(10, 4), facecolor='white')
ax.plot(historial['hora'], historial['temperatura'], marker='o', linewidth=2, markersize=6, color='tab:blue')
ax.axhline(UMBRAL_TEMPERATURA, color='red', linestyle='--', label='Umbral crítico')
ax.set_xlabel("Hora")
ax.set_ylabel("Temperatura (°C)")
ax.legend()
st.pyplot(fig)


# --- GUARDAR EN GOOGLE SHEETS ---
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
    import json
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_dict), scope)
    client = gspread.authorize(creds)

    sheet = client.open("monitor_ia_datos").sheet1
    sheet.append_row([dato['hora'], dato['temperatura'], str(dato['vibracion'])], value_input_option='USER_ENTERED')

except Exception as e:
    st.warning(f"No se pudo guardar en Google Sheets: {e}")

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
