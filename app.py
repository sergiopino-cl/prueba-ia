import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

from database import init_db, add_server, get_servers, delete_server, log_check, get_latest_status, get_history
from monitor import check_url

# Configuración de la página
st.set_page_config(
    page_title="Monitor de Páginas Web & Servidores",
    page_icon="📡",
    layout="wide"
)

# Inicializar base de datos
init_db()

st.title("📡 Monitor de Estado de Páginas Web y Servidores")
st.markdown("Supervisa la disponibilidad, tiempos de respuesta y mantén un histórico detallado de tus sitios web en SQLite.")

# Sidebar de Navegación
st.sidebar.header("Menú Principal")
menu = st.sidebar.radio(
    "Selecciona una opción:",
    ["📊 Dashboard General", "➕ Administrar Servidores", "📈 Histórico y Gráficas"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Acciones Rápidas")

if st.sidebar.button("🔄 Verificar Todos los Servidores Ahora"):
    servers_df = get_servers()
    if servers_df.empty:
        st.sidebar.warning("No hay servidores registrados.")
    else:
        with st.spinner("Comprobando estado de todos los servidores..."):
            for _, row in servers_df.iterrows():
                status_code, resp_time, is_up, err_msg = check_url(row['url'])
                log_check(row['id'], status_code, resp_time, is_up, err_msg)
        st.sidebar.success("¡Verificación completada!")
        st.rerun()

# ----------------------------------------------------
# 1. DASHBOARD GENERAL
# ----------------------------------------------------
if menu == "📊 Dashboard General":
    st.header("📊 Estado Actual de Servidores")
    
    status_df = get_latest_status()
    
    if status_df.empty:
        st.info("No hay servidores registrados. Ve a la sección **'Administrar Servidores'** para agregar el primero.")
    else:
        # Métricas generales
        total_servers = len(status_df)
        up_servers = len(status_df[status_df['is_up'] == 1])
        down_servers = len(status_df[(status_df['is_up'] == 0) & (status_df['is_up'].notnull())])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Servidores", total_servers)
        col2.metric("En Línea (UP)", up_servers, delta=f"{up_servers}/{total_servers}")
        col3.metric("Caídos (DOWN)", down_servers, delta=f"-{down_servers}" if down_servers > 0 else "0", delta_color="inverse")
        
        st.markdown("---")
        
        # Tarjetas de estado por servidor
        for _, row in status_df.iterrows():
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([2, 3, 1, 1, 1])
                
                with c1:
                    st.markdown(f"**{row['name']}**")
                with c2:
                    st.markdown(f"[{row['url']}]({row['url']})")
                with c3:
                    if row['is_up'] == 1:
                        st.success("🟢 UP")
                    elif row['is_up'] == 0:
                        st.error("🔴 DOWN")
                    else:
                        st.info("⚪ Sin verificar")
                with c4:
                    rt = f"{row['response_time_ms']} ms" if pd.notnull(row['response_time_ms']) else "-"
                    st.text(f"⏱️ {rt}")
                with c5:
                    sc = f"HTTP {int(row['status_code'])}" if pd.notnull(row['status_code']) else "-"
                    st.text(sc)
                
                if pd.notnull(row['timestamp']):
                    st.caption(f"Última verificación: {row['timestamp']} | Intervalo: cada {row['interval_seconds']}s")
                st.markdown("---")

        # Gráfica rápida de tiempos de respuesta recientes
        st.subheader("⏱️ Tiempos de Respuesta Recientes")
        history_df = get_history(hours=6)
        if not history_df.empty:
            fig = px.line(
                history_df, 
                x='timestamp', 
                y='response_time_ms', 
                color='name',
                markers=True,
                labels={'timestamp': 'Hora', 'response_time_ms': 'Tiempo de Respuesta (ms)', 'name': 'Servidor'},
                title="Historial de Tiempos de Respuesta (Últimas 6 horas)"
            )
            fig.update_layout(xaxis_title="Hora", yaxis_title="Milisegundos (ms)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ejecuta una verificación para ver las gráficas de rendimiento.")

# ----------------------------------------------------
# 2. ADMINISTRAR SERVIDORES
# ----------------------------------------------------
elif menu == "➕ Administrar Servidores":
    st.header("➕ Agregar o Eliminar Servidores")
    
    with st.form("add_server_form", clear_on_submit=True):
        st.subheader("Registrar Nueva Página Web")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nombre del Servidor / Sitio", placeholder="Ej: Google, Mi API, Blog")
            url = st.text_input("URL de la Webpage", placeholder="https://ejemplo.com")
        with col2:
            interval_minutes = st.number_input("Intervalo de verificación (minutos)", min_value=1, max_value=1440, value=5)
            
        submitted = st.form_submit_button("Guardar y Verificar Servidor")
        
        if submitted:
            if not name or not url:
                st.error("Por favor completa el nombre y la URL.")
            else:
                interval_seconds = int(interval_minutes * 60)
                success, server_id, msg = add_server(name, url, interval_seconds)
                if success:
                    st.success(msg)
                    # Realizar primer chequeo inmediato
                    with st.spinner("Realizando primera verificación..."):
                        status_code, resp_time, is_up, err_msg = check_url(url)
                        log_check(server_id, status_code, resp_time, is_up, err_msg)
                    st.success("¡Verificación inicial guardada en SQLite!")
                    st.rerun()
                else:
                    st.error(msg)
                    
    st.markdown("---")
    st.subheader("📋 Listado de Servidores Registrados")
    servers_df = get_servers()
    
    if servers_df.empty:
        st.info("No hay servidores registrados.")
    else:
        for _, row in servers_df.iterrows():
            c1, c2, c3, c4 = st.columns([2, 3, 2, 1])
            with c1:
                st.write(f"**{row['name']}**")
            with c2:
                st.write(row['url'])
            with c3:
                st.write(f"Intervalo: {row['interval_seconds'] // 60} min")
            with c4:
                if st.button("🗑️ Eliminar", key=f"del_{row['id']}"):
                    delete_server(row['id'])
                    st.success(f"Servidor {row['name']} eliminado.")
                    st.rerun()

# ----------------------------------------------------
# 3. HISTÓRICO Y GRÁFICAS
# ----------------------------------------------------
elif menu == "📈 Histórico y Gráficas":
    st.header("📈 Histórico de Verificaciones (SQLite - Último Mes)")
    
    servers_df = get_servers()
    if servers_df.empty:
        st.info("No hay servidores registrados para mostrar históricos.")
    else:
        server_options = {"Todos los servidores": None}
        for _, row in servers_df.iterrows():
            server_options[row['name']] = row['id']
            
        selected_server_name = st.selectbox("Filtrar por servidor:", list(server_options.keys()))
        selected_server_id = server_options[selected_server_name]
        
        hours_filter = st.selectbox(
            "Rango de tiempo:",
            options=[6, 12, 24, 72, 168, 720],
            format_func=lambda x: f"Últimas {x} horas" if x < 720 else "Último mes (720 horas)",
            index=2 # por defecto 24 horas
        )
        
        history_df = get_history(server_id=selected_server_id, hours=hours_filter)
        
        if history_df.empty:
            st.warning("No hay registros históricos para el filtro seleccionado.")
        else:
            # Gráfica de tiempos de respuesta
            st.subheader("📉 Evolución del Tiempo de Respuesta")
            fig_time = px.line(
                history_df,
                x='timestamp',
                y='response_time_ms',
                color='name',
                markers=True,
                labels={'timestamp': 'Fecha y Hora', 'response_time_ms': 'Tiempo (ms)', 'name': 'Servidor'}
            )
            st.plotly_chart(fig_time, use_container_width=True)
            
            # Gráfica de disponibilidad (Estado UP/DOWN)
            st.subheader("📊 Disponibilidad (Estado)")
            fig_status = px.scatter(
                history_df,
                x='timestamp',
                y='is_up',
                color='name',
                symbol='is_up',
                labels={'timestamp': 'Fecha y Hora', 'is_up': 'Estado (1=UP, 0=DOWN)', 'name': 'Servidor'},
                title="Historial de Estado de Conexión"
            )
            st.plotly_chart(fig_status, use_container_width=True)
            
            st.markdown("---")
            st.subheader("📋 Tabla de Registros Detallados")
            st.dataframe(history_df[['timestamp', 'name', 'url', 'status_code', 'response_time_ms', 'is_up', 'error_message']], use_container_width=True)
            
            # Botón de exportación a CSV
            csv = history_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Histórico en CSV",
                data=csv,
                file_name=f"historico_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv',
            )
