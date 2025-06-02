import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar el archivo CSV con los casos resueltos
df_casos = pd.read_csv("casos.csv")

# Convertir fechas si es necesario
df_casos['Fecha/Hora de cierre'] = pd.to_datetime(df_casos['Fecha/Hora de cierre'], errors='coerce')

# Eliminar casos sin 'Propietario al cierre'
df_casos = df_casos[df_casos['Propietario al cierre'].notna()]
df_casos = df_casos[df_casos['Propietario al cierre'].str.strip() != ""]

# Sidebar para seleccionar agentes
agentes = sorted(df_casos['Propietario al cierre'].unique())
seleccion = st.multiselect("Selecciona agente(s):", agentes, default=agentes)

# Filtrar DataFrame
df_filtrado = df_casos[df_casos['Propietario al cierre'].isin(seleccion)]

# Agrupar por agente
conteo = df_filtrado['Propietario al cierre'].value_counts().reset_index()
conteo.columns = ['Agente', 'Casos cerrados']

# Título
st.title("Casos cerrados por agente")

# Gráfico
plt.figure(figsize=(10, 6))
sns.barplot(data=conteo, x='Casos cerrados', y='Agente', palette='Blues_d')
plt.xlabel("Número de casos cerrados")
plt.ylabel("Agente")
st.pyplot(plt)
