import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
frecuencia_opcion = st.selectbox("Selecciona la frecuencia de agrupación:", list(frecuencia_map.keys()))
frecuencia = frecuencia_map[frecuencia_opcion]

# Selector de vista
vista = st.radio("¿Qué deseas visualizar?", options=["Casos cerrados", "Casos asignados", "Ambos"])

if vista in ["Casos cerrados", "Ambos"]:
    # =========================
    # CASOS CERRADOS por agente
    # =========================
    agentes_cierre = sorted(df_casos['Propietario al cierre'].unique())
    agentes_sel_cierre = st.multiselect("Selecciona agente(s) - Casos cerrados:", agentes_cierre, default=agentes_cierre)
    df_casos_filtrado = df_casos[df_casos['Propietario al cierre'].isin(agentes_sel_cierre)]
    df_casos_filtrado.set_index('Fecha/Hora de cierre', inplace=True)
    df_casos_grouped = df_casos_filtrado.groupby([
        pd.Grouper(freq=frecuencia, label='left'),
        'Propietario al cierre'
    ]).size().reset_index(name='Casos cerrados')

    st.title("Casos cerrados por agente")
    plt.figure(figsize=(12, 6))
    lineplot = sns.lineplot(data=df_casos_grouped, x='Fecha/Hora de cierre', y='Casos cerrados', hue='Propietario al cierre', marker='o')
    plt.xlabel("Fecha")
    plt.ylabel("Casos cerrados")
    plt.title(f"Casos cerrados ({frecuencia_opcion.lower()}) por agente")
    plt.xticks(rotation=45)
    plt.legend(title="Agente")
    for line in lineplot.lines:
        for x, y in zip(line.get_xdata(), line.get_ydata()):
            if not pd.isna(y):
                plt.text(x, y, f'{int(y)}', fontsize=8, ha='center', va='bottom')
    st.pyplot(plt)
    df_casos_filtrado.reset_index(inplace=True)

if vista in ["Casos asignados", "Ambos"]:
    # =========================
    # CASOS ASIGNADOS por agente
    # =========================
    agentes_asignados = sorted(df_ftes['kavako_asig'].unique())
    agentes_sel_asignados = st.multiselect("Selecciona agente(s) - Casos asignados:", agentes_asignados, default=agentes_asignados)
    df_ftes_filtrado = df_ftes[df_ftes['kavako_asig'].isin(agentes_sel_asignados)]
    df_ftes_filtrado.set_index('fecha_asig', inplace=True)
    df_asignados_grouped = df_ftes_filtrado.groupby([
        pd.Grouper(freq=frecuencia, label='left'),
        'kavako_asig'
    ]).size().reset_index(name='Casos asignados')

    st.title("Casos asignados por agente")
    plt.figure(figsize=(12, 6))
    lineplot2 = sns.lineplot(data=df_asignados_grouped, x='fecha_asig', y='Casos asignados', hue='kavako_asig', marker='o')
    plt.xlabel("Fecha")
    plt.ylabel("Casos asignados")
    plt.title(f"Casos asignados ({frecuencia_opcion.lower()}) por agente")
    plt.xticks(rotation=45)
    plt.legend(title="Agente")
    for line in lineplot2.lines:
        for x, y in zip(line.get_xdata(), line.get_ydata()):
            if not pd.isna(y):
                plt.text(x, y, f'{int(y)}', fontsize=8, ha='center', va='bottom')
    st.pyplot(plt)
    df_ftes_filtrado.reset_index(inplace=True)
