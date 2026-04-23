import sqlite3
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_name: str = "reporter.db"):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_string TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_data TEXT NOT NULL,
                target_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_session(self, session_string: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sessions (session_string) VALUES (?)", (session_string,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_sessions(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, session_string FROM sessions")
        sessions = [{"id": row[0], "session_string": row[1]} for row in cursor.fetchall()]
        conn.close()
        return sessions
    
    def delete_session(self, session_id: int) -> bool:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        result = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return result
    
    def get_session_count(self) -> int:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sessions")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def set_target(self, target_data: str, target_type: str) -> bool:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM targets")
        cursor.execute("INSERT INTO targets (target_data, target_type) VALUES (?, ?)", 
                      (target_data, target_type))
        conn.commit()
        conn.close()
        return True
    
    def get_target(self) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT target_data, target_type FROM targets LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        if result:
            return {"data": result[0], "type": result[1]}
        return None
