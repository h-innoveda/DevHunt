import json
from core.db import get_db_connection


def log(level: str, category: str, message: str, metadata: dict = None):
    """
    Write a log entry to system_logs table.
    level    : INFO | WARN | ERROR | SUCCESS
    category : api_call | key_event | chat | rag | backup | system
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO system_logs (level, category, message, metadata) VALUES (?, ?, ?, ?)",
            (level, category, message, json.dumps(metadata or {}))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        # Never crash the app because of logging
        print(f"[LOGGER ERROR] {e}")


def info(category: str, message: str, metadata: dict = None):
    log("INFO", category, message, metadata)


def success(category: str, message: str, metadata: dict = None):
    log("SUCCESS", category, message, metadata)


def warn(category: str, message: str, metadata: dict = None):
    log("WARN", category, message, metadata)


def error(category: str, message: str, metadata: dict = None):
    log("ERROR", category, message, metadata)


def get_logs(limit: int = 200, level: str = None, category: str = None) -> list:
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM system_logs"
    params = []
    conditions = []

    if level:
        conditions.append("level = ?")
        params.append(level)
    if category:
        conditions.append("category = ?")
        params.append(category)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        row = dict(r)
        try:
            row['metadata'] = json.loads(row['metadata'])
        except Exception:
            row['metadata'] = {}
        result.append(row)
    return result
