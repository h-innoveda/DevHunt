import json
from datetime import datetime
from core.db import get_db_connection

class TodoManager:
    @staticmethod
    def get_todos(status_filter=None, priority_filter=None, source_filter=None) -> list:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT id, title, description, priority, status, due_date, tags, source, created_at, completed_at FROM todos WHERE 1=1"
        params = []
        
        if status_filter:
            query += " AND status = ?"
            params.append(status_filter)
        if priority_filter:
            query += " AND priority = ?"
            params.append(priority_filter)
        if source_filter:
            query += " AND source = ?"
            params.append(source_filter)
            
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        todos = []
        for r in rows:
            todo_dict = dict(r)
            try:
                todo_dict['tags'] = json.loads(todo_dict['tags']) if todo_dict['tags'] else []
            except Exception:
                todo_dict['tags'] = []
            todos.append(todo_dict)
            
        return todos

    @staticmethod
    def create_todo(title: str, description: str = "", priority: str = "medium", 
                    status: str = "pending", due_date: str = None, tags: list = None, 
                    source: str = "manual") -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        tags_str = json.dumps(tags if tags else [])
        now_str = datetime.now().isoformat()
        
        cursor.execute(
            """INSERT INTO todos (title, description, priority, status, due_date, tags, source, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, description, priority, status, due_date, tags_str, source, now_str)
        )
        todo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "id": todo_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": status,
            "due_date": due_date,
            "tags": tags if tags else [],
            "source": source,
            "created_at": now_str,
            "completed_at": None
        }

    @staticmethod
    def update_todo(todo_id: int, updates: dict) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        fields = []
        params = []
        
        for k, v in updates.items():
            if k in ['title', 'description', 'priority', 'status', 'due_date', 'source']:
                fields.append(f"{k} = ?")
                params.append(v)
                
                # If marking as done, set completed_at
                if k == 'status' and v == 'done':
                    fields.append("completed_at = ?")
                    params.append(datetime.now().isoformat())
                elif k == 'status' and v != 'done':
                    fields.append("completed_at = NULL")
            elif k == 'tags' and isinstance(v, list):
                fields.append("tags = ?")
                params.append(json.dumps(v))
                
        if not fields:
            conn.close()
            return False
            
        params.append(todo_id)
        query = f"UPDATE todos SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        
        return rowcount > 0

    @staticmethod
    def delete_todo(todo_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0

    @staticmethod
    def complete_todo(todo_id: int) -> bool:
        return TodoManager.update_todo(todo_id, {"status": "done"})
