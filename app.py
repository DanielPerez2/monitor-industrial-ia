
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Debug detallado Google Sheets", layout="centered")
st.title("🧪 Prueba de conexión a Google Sheets")

st.markdown("Esta app muestra paso a paso la conexión a Google Sheets con mensajes visibles.")

try:
    st.subheader("🔐 1. Cargando archivo JSON de credenciales...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    st.write("Usando archivo: `apt-tracker-463114-h7-83eb18660572.json`")
    creds = ServiceAccountCredentials.from_json_keyfile_name("apt-tracker-463114-h7-83eb18660572.json", scope)
    st.success("✅ Credenciales cargadas correctamente.")
    st.code(creds.service_account_email)

    st.subheader("🔗 2. Autenticando con Google Sheets...")
    client = gspread.authorize(creds)
    st.success("✅ Autenticación correcta.")
    st.write(client)

    st.subheader("📄 3. Abriendo hoja: `monitor_ia_datos`...")
    sheet = client.open("monitor_ia_datos").sheet1
    st.success("✅ Hoja abierta correctamente.")
    st.write(f"Primera fila de la hoja: {sheet.row_values(1)}")

    st.subheader("📊 4. Cargando datos de la hoja...")
    datos = sheet.get_all_records()
    df = pd.DataFrame(datos)
    st.success("✅ Datos cargados correctamente:")
    st.dataframe(df)

except Exception as e:
    st.error("❌ Error detectado en algún paso:")
    st.code(str(e), language="python")
