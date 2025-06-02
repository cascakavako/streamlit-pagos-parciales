import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# =========================
# Cargar CASOS CERRADOS
# =========================
df_casos = pd.read_csv("casos.csv")
df_casos['Fecha/Hora de cierre'] = pd.to_datetime(df_casos['Fecha/Hora de cierre'], errors='coerce')
df_casos['Propietario al cierre'] = df_casos['Propietario al cierre'].astype(str).str.strip().str.title()
df_casos = df_casos[df_casos['Propietario al cierre'].notna()]
df_casos = df_casos[df_casos['Propietario al cierre'].str.len() > 0]

# =========================
# Cargar FTEs (asignaciones)
# =========================
df_ftes = pd.read_csv("ftes.csv", skiprows=1)
df_ftes['fecha_asig'] = pd.to_datetime(df_ftes['fecha_asig'], errors='coerce')
df_ftes['kavako_asig'] = df_ftes['kavako_asig'].astype(str).str.strip().str.title()
df_ftes = df_ftes[df_ftes['kavako_asig'].notna()]
df_ftes = df_ftes[df_ftes['kavako_asig'].str.len() > 0]

# =========================
# Sidebar general
# =========================
frecuencia_map = {
    'Diaria': 'D',
    'Semanal': 'W',
    'Mensual': 'M'
}
frecuencia_opcion = st.sidebar.selectbox("Selecciona la frecuencia de agrupación:", list(frecuencia_map.keys()))
frecuencia = frecuencia_map[frecuencia_opcion]

# Calcular fecha de corte según la frecuencia
hoy = datetime.today()
if frecuencia == 'D':
    fecha_min = hoy - timedelta(days=90)
elif frecuencia == 'W':
    fecha_min = hoy - timedelta(weeks=16)
else:
    fecha_min = pd.to_datetime("2024-01-01")

# Selector de vista
vista = st.sidebar.radio("¿Qué deseas visualizar?", options=["Casos cerrados", "Casos asignados", "Ambos"])

# =========================
# Selector unificado de agentes
# =========================
agentes_unicos = sorted(set(df_casos['Propietario al cierre']).union(set(df_ftes['kavako_asig'])))
agentes_sel = st.sidebar.multiselect("Selecciona agente(s):", agentes_unicos, default=agentes_unicos)

# =========================
# Filtrado y agrupación
# =========================
df_casos_filtrado = df_casos[(df_casos['Propietario al cierre'].isin(agentes_sel)) & (df_casos['Fecha/Hora de cierre'] >= fecha_min)]
df_casos_filtrado.set_index('Fecha/Hora de cierre', inplace=True)
df_casos_grouped = df_casos_filtrado.groupby([
    pd.Grouper(freq=frecuencia, label='left'),
    'Propietario al cierre'
]).size().reset_index(name='Casos cerrados')
df_casos_filtrado.reset_index(inplace=True)

df_ftes_filtrado = df_ftes[(df_ftes['kavako_asig'].isin(agentes_sel)) & (df_ftes['fecha_asig'] >= fecha_min)]
df_ftes_filtrado.set_index('fecha_asig', inplace=True)
df_asignados_grouped = df_ftes_filtrado.groupby([
    pd.Grouper(freq=frecuencia, label='left'),
    'kavako_asig'
]).size().reset_index(name='Casos asignados')
df_ftes_filtrado.reset_index(inplace=True)

# =========================
# Visualización combinada
# =========================
if vista == "Ambos":
    st.title("Casos cerrados y asignados por agente")
    plt.figure(figsize=(12, 6))

    # Línea sólida: casos cerrados
    for agente in agentes_sel:
        data_cierre = df_casos_grouped[df_casos_grouped['Propietario al cierre'] == agente]
        plt.plot(data_cierre['Fecha/Hora de cierre'], data_cierre['Casos cerrados'], label=f"Cerrados - {agente}", marker='o', linestyle='-')

    # Línea punteada: casos asignados
    for agente in agentes_sel:
        data_asig = df_asignados_grouped[df_asignados_grouped['kavako_asig'] == agente]
        plt.plot(data_asig['fecha_asig'], data_asig['Casos asignados'], label=f"Asignados - {agente}", marker='o', linestyle='--')

    plt.xlabel("Fecha")
    plt.ylabel("Cantidad de casos")
    plt.title(f"Casos cerrados y asignados ({frecuencia_opcion.lower()}) por agente")
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot(plt)

elif vista == "Casos cerrados":
    st.title("Casos cerrados por agente")
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_casos_grouped, x='Fecha/Hora de cierre', y='Casos cerrados', hue='Propietario al cierre', marker='o')
    plt.xlabel("Fecha")
    plt.ylabel("Casos cerrados")
    plt.title(f"Casos cerrados ({frecuencia_opcion.lower()}) por agente")
    plt.xticks(rotation=45)
    plt.legend(title="Agente")
    st.pyplot(plt)

elif vista == "Casos asignados":
    st.title("Casos asignados por agente")
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_asignados_grouped, x='fecha_asig', y='Casos asignados', hue='kavako_asig', marker='o', linestyle='--')
    plt.xlabel("Fecha")
    plt.ylabel("Casos asignados")
    plt.title(f"Casos asignados ({frecuencia_opcion.lower()}) por agente")
    plt.xticks(rotation=45)
    plt.legend(title="Agente")
    st.pyplot(plt)
