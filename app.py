
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Debug conexión Google Sheets", layout="centered")
st.title("🔧 Depuración de conexión con Google Sheets")

try:
    st.markdown("### Paso 1: Cargando credenciales")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("apt-tracker-463114-h7-83eb18660572.json", scope)

    st.success("✅ Credenciales cargadas correctamente")

    st.markdown("### Paso 2: Conectando con Google Sheets")
    client = gspread.authorize(creds)
    sheet = client.open("monitor_ia_datos").sheet1

    st.success("✅ Conexión con Google Sheets exitosa")

    st.markdown("### Paso 3: Leyendo datos de la hoja")
    datos = sheet.get_all_records()
    historial = pd.DataFrame(datos)

    st.dataframe(historial)

except Exception as e:
    st.error("❌ Se ha producido un error:")
    st.code(str(e), language="python")
