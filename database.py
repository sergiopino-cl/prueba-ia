import sqlite3
from datetime import datetime, timedelta
import pandas as pd

DB_NAME = "monitor.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla de servidores / páginas web
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            interval_seconds INTEGER DEFAULT 60,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla de histórico de verificaciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status_code INTEGER,
            response_time_ms REAL,
            is_up INTEGER,
            error_message TEXT,
            FOREIGN KEY (server_id) REFERENCES servers (id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def add_server(name, url, interval_seconds):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO servers (name, url, interval_seconds) VALUES (?, ?, ?)",
            (name, url, interval_seconds)
        )
        conn.commit()
        server_id = cursor.lastrowid
        return True, server_id, "Servidor agregado con éxito."
    except sqlite3.IntegrityError:
        return False, None, "La URL ya está registrada."
    except Exception as e:
        return False, None, str(e)
    finally:
        conn.close()

def get_servers():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM servers ORDER BY created_at DESC", conn)
    conn.close()
    return df

def delete_server(server_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM checks WHERE server_id = ?", (server_id,))
    cursor.execute("DELETE FROM servers WHERE id = ?", (server_id,))
    conn.commit()
    conn.close()

def log_check(server_id, status_code, response_time_ms, is_up, error_message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO checks (server_id, timestamp, status_code, response_time_ms, is_up, error_message)
        VALUES (?, datetime('now', 'localtime'), ?, ?, ?, ?)
    """, (server_id, status_code, response_time_ms, 1 if is_up else 0, error_message))
    conn.commit()
    
    # Limpiar registros con más de 30 días para mantener la base de datos optimizada
    cursor.execute("""
        DELETE FROM checks WHERE timestamp < datetime('now', '-30 days')
    """)
    conn.commit()
    conn.close()

def get_latest_status():
    conn = get_connection()
    query = """
        SELECT s.id, s.name, s.url, s.interval_seconds, 
               c.timestamp, c.status_code, c.response_time_ms, c.is_up, c.error_message
        FROM servers s
        LEFT JOIN checks c ON s.id = c.server_id
        WHERE c.id IN (
            SELECT MAX(id) FROM checks GROUP BY server_id
        )
        UNION
        SELECT s.id, s.name, s.url, s.interval_seconds, 
               NULL as timestamp, NULL as status_code, NULL as response_time_ms, NULL as is_up, NULL as error_message
        FROM servers s
        WHERE s.id NOT IN (SELECT DISTINCT server_id FROM checks)
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_history(server_id=None, hours=24):
    conn = get_connection()
    if server_id:
        query = f"""
            SELECT c.*, s.name, s.url 
            FROM checks c
            JOIN servers s ON c.server_id = s.id
            WHERE c.server_id = ? AND c.timestamp >= datetime('now', '-{hours} hours', 'localtime')
            ORDER BY c.timestamp DESC
        """
        df = pd.read_sql(query, conn, params=(server_id,))
    else:
        query = f"""
            SELECT c.*, s.name, s.url 
            FROM checks c
            JOIN servers s ON c.server_id = s.id
            WHERE c.timestamp >= datetime('now', '-{hours} hours', 'localtime')
            ORDER BY c.timestamp DESC
        """
        df = pd.read_sql(query, conn)
    conn.close()
    return df
