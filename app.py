import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Prueba IA - Streamlit App",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Bienvenido a Prueba IA")
st.markdown("Esta es una aplicación de prueba desarrollada en **Streamlit** con asistencia de Inteligencia Artificial.")

# Sidebar
st.sidebar.header("Panel de Configuración")
nombre = st.sidebar.text_input("¿Cómo te llamas?", "Usuario")
opcion = st.sidebar.selectbox(
    "Elige una sección:",
    ["🏠 Inicio", "📊 Análisis de Datos", "⚙️ Configuración"]
)

if "🏠 Inicio" in opcion:
    st.subheader(f"¡Hola, {nombre}! 👋")
    st.write("Usa la barra lateral para navegar entre las distintas secciones de esta aplicación de prueba.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Modelo IA", value="Gemini 3.5 Flash", delta="High Reasoning")
    with col2:
        st.metric(label="Framework", value="Streamlit", delta="v1.x")
    with col3:
        st.metric(label="Estado", value="Activo", delta="100%")

elif "📊 Análisis de Datos" in opcion:
    st.subheader("📊 Generación y Análisis de Datos de Prueba")
    
    num_puntos = st.slider("Número de puntos de datos:", 10, 500, 100)
    
    # Generar datos aleatorios
    df = pd.DataFrame({
        'x': np.arange(num_puntos),
        'y': np.randn(num_puntos).cumsum() + 50
    })
    
    st.line_chart(df.set_index('x'))
    
    if st.checkbox("Mostrar tabla de datos"):
        st.dataframe(df)

else:
    st.subheader("⚙️ Configuración de la Aplicación")
    st.write("Aquí puedes ajustar parámetros avanzados de tu aplicación de Streamlit.")
    tema_oscuro = st.checkbox("Modo Oscuro / Preferencia guardada", value=True)
    st.success("Configuración cargada correctamente.")

st.markdown("---")
st.caption("Desarrollado con ❤️ usando Python, Streamlit y pi (AI Coding Assistant).")
