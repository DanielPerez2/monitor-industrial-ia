import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib  # Para guardar el modelo

# Cargar historial
df = pd.read_csv('historial_datos.csv')

# Solo usamos las columnas numéricas para entrenar
X = df[['temperatura', 'vibracion']]

# Entrenar modelo Isolation Forest
modelo = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
modelo.fit(X)

# Predecir si cada muestra es normal (1) o anómala (-1)
df['anomalia'] = modelo.predict(X)

# Mostrar resultados
print(df.tail())

# Guardar el modelo entrenado
joblib.dump(modelo, 'modelo_ia.joblib')
print("✅ Modelo guardado como modelo_ia.joblib")

# Cargar modelo
modelo = joblib.load('modelo_ia.joblib')

# Simulamos una nueva lectura
nueva_temp = 75
nueva_vibra = 1
nueva_entrada = [[nueva_temp, nueva_vibra]]

# Predecir
resultado = modelo.predict(nueva_entrada)

if resultado[0] == -1:
    print("⚠️ Anomalía detectada")
else:
    print("✅ Todo normal")


