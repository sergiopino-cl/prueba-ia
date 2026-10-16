import time
requests_try = True
try:
    import requests
except ImportError:
    requests_try = False

def check_url(url):
    """
    Realiza una petición HTTP GET a la URL y mide el tiempo de respuesta.
    Retorna: (status_code, response_time_ms, is_up, error_message)
    """
    start_time = time.time()
    try:
        # Asegurar que la URL tenga esquema
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        response = requests.get(url, timeout=10, headers={"User-Agent": "StreamlitMonitor/1.0"})
        end_time = time.time()
        
        response_time_ms = round((end_time - start_time) * 1000, 2)
        status_code = response.status_code
        
        # Consideramos UP si el código de estado es menor que 400 (o 200-399)
        is_up = 200 <= status_code < 400
        error_message = None if is_up else f"HTTP Status: {status_code}"
        
        return status_code, response_time_ms, is_up, error_message

    except requests.exceptions.Timeout:
        end_time = time.time()
        response_time_ms = round((end_time - start_time) * 1000, 2)
        return None, response_time_ms, False, "Timeout de conexión (>10s)"
    
    except requests.exceptions.ConnectionError:
        end_time = time.time()
        response_time_ms = round((end_time - start_time) * 1000, 2)
        return None, response_time_ms, False, "Error de conexión (Host no encontrado)"
        
    except Exception as e:
        end_time = time.time()
        response_time_ms = round((end_time - start_time) * 1000, 2)
        return None, response_time_ms, False, str(e)
