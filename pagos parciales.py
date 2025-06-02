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

# Selector de frecuencia
frecuencia_map = {
    'Diaria': 'D',
    'Semanal': 'W',
    'Mensual': 'M'
}
frecuencia_opcion = st.selectbox("Selecciona la frecuencia de agrupación:", list(frecuencia_map.keys()))
frecuencia = frecuencia_map[frecuencia_opcion]

# Filtrar DataFrame por agentes seleccionados
df_filtrado = df_casos[df_casos['Propietario al cierre'].isin(seleccion)]

# Agrupar por fecha según frecuencia
df_filtrado.set_index('Fecha/Hora de cierre', inplace=True)
df_grouped = df_filtrado.groupby([pd.Grouper(freq=frecuencia), 'Propietario al cierre']).size().reset_index(name='Casos cerrados')

# Título
st.title("Casos cerrados por agente")

# Gráfico de líneas con anotaciones
plt.figure(figsize=(12, 6))
lineplot = sns.lineplot(data=df_grouped, x='Fecha/Hora de cierre', y='Casos cerrados', hue='Propietario al cierre', marker='o')
plt.xlabel("Fecha")
plt.ylabel("Casos cerrados")
plt.title(f"Casos cerrados ({frecuencia_opcion.lower()}) por agente")
plt.xticks(rotation=45)

# Agregar etiquetas en los puntos
for line in lineplot.lines:
    for x, y in zip(line.get_xdata(), line.get_ydata()):
        if not pd.isna(y):
            plt.text(x, y, f'{int(y)}', fontsize=8, ha='center', va='bottom')

st.pyplot(plt)

# Restaurar índice por si se usa más adelante
df_filtrado.reset_index(inplace=True)
