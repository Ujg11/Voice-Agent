import sqlite3 # database
from pathlib import Path
from typing import List, Tuple

DB_PATH = Path(__file__).resolve().parents[1] / "conversations.db"

# Init database si no existeix
def init_db():
	with sqlite3.connect(DB_PATH) as conn:
		conn.execute("""
			CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_text TEXT NOT NULL,
                agent_reply TEXT NOT NULL,
                language TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
		""")

# Guarda un missatge a la DB
def save_message(session_id: str, user_text: str, agent_reply: str, language: str):
	with sqlite3.connect(DB_PATH) as conn:
		conn.execute(
			"INSERT INTO conversations (session_id, user_text, agent_reply, language) VALUES (?, ?, ?, ?)",
			(session_id, user_text, agent_reply, language)
)

# Obté els últims missatges de la sessió	
def get_recent_messages(session_id: str, limit: int = 10):
	with sqlite3.connect(DB_PATH) as conn:
		cursor = conn.execute(
			"SELECT user_text, agent_reply, language FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
			(session_id, limit)
		)
		return list(cursor.fetchall())[::-1] #invertim