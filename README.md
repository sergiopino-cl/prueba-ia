# Prueba IA - Streamlit Application & Web Monitor

Aplicación web interactiva desarrollada con **Streamlit** y Python para supervisar el estado de páginas web y servidores con histórico en SQLite.

## 🚀 Características
- Dashboard en tiempo real (UP/DOWN, tiempos de respuesta).
- Gestión de servidores y URLs personalizadas.
- Histórico de hasta 1 mes guardado en SQLite y gráficas con Plotly.
- Soporte completo para ejecución local y despliegue en **Docker**.

---

## 🐳 Despliegue con Docker y Docker Compose (Recomendado para Servidores)

1. Asegúrate de tener instalado **Docker** y **Docker Compose** en tu servidor.
2. Clona el repositorio y entra a la carpeta:
   ```bash
   cd Dev/prueba-ia
   ```
3. Construye y levanta el contenedor en segundo plano:
   ```bash
   docker compose up --build -d
   ```
4. Accede a tu aplicación en el navegador:
   ```text
   http://<IP_DE_TU_SERVIDOR>:8501
   ```

Para ver los logs o detener la aplicación:
```bash
# Ver logs
docker compose logs -f

# Detener aplicación
docker compose down
```

---

## 📦 Instalación Local (Desarrollo)

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta la aplicación de Streamlit:
   ```bash
   python -m streamlit run app.py
   ```

---
Desarrollado con asistencia de **pi** (AI Coding Assistant).
