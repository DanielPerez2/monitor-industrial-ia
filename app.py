import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="Debug Final Google Sheets", layout="centered")
st.title("🛠 Debug Final - Google Sheets")

try:
    st.subheader("1️⃣ Cargando credenciales...")
    import json
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    cred_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, scope)

    st.success("✅ Credenciales cargadas correctamente")

    st.subheader("2️⃣ Autenticando cliente...")
    client = gspread.authorize(creds)
    st.success("✅ Cliente autorizado")

    st.subheader("3️⃣ Listando documentos disponibles en tu Google Drive:")
    docs = client.openall()
    for doc in docs:
        st.markdown(f"- {doc.title}")

    st.subheader("4️⃣ Intentando abrir hoja 'monitor_ia_datos'...")
    try:
        sheet = client.open("monitor_ia_datos").sheet1
        st.success("✅ Hoja encontrada correctamente")
        st.code(f"Nombre hoja: {sheet.title}")

        st.subheader("5️⃣ Insertando fila de prueba...")
        hora = datetime.now().strftime("%H:%M:%S")
        temperatura = 42.0
        vibracion = True
        index = len(sheet.get_all_values()) + 1
        sheet.append_row([hora, temperatura, str(vibracion)], value_input_option='USER_ENTERED')
        st.success(f"📤 Fila insertada correctamente en la fila {index}")
        st.write("Contenido insertado:")
        st.write({"hora": hora, "temperatura": temperatura, "vibracion": vibracion})

    except Exception as sheet_error:
        st.error("❌ No se pudo abrir o escribir en la hoja 'monitor_ia_datos'")
        st.code(str(sheet_error))

except Exception as e:
    st.error("❌ Error general:")
    st.code(str(e))

