import sqlite3
from datetime import datetime


class RokaDatabase:
    def __init__(self, db_path="roka_mem.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        affection_query = """
            CREATE TABLE IF NOT EXISTS affection
            (
              user_id TEXT PRIMARY KEY,
              affection_level INTEGER
            ) 
            """

        chat_history_query = """
            CREATE TABLE IF NOT EXISTS chat_history 
            ( 
             user_id TEXT, 
             speaker TEXT,
             message TEXT, 
             text_time DATETIME
            ) 
            """

        cursor.execute(affection_query)
        cursor.execute(chat_history_query)
        conn.commit()
        conn.close()
        print("init roka mem database")

    def _execute_query(self, query, params=(), fetch_type=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(query, params)

        if fetch_type == "one":
            result = cursor.fetchone()
        elif fetch_type == "all":
            result = cursor.fetchall()
        elif fetch_type == "rowcount":
            result = cursor.rowcount
        else:
            result = None

        conn.commit()
        conn.close()

        return result

    def save_affection(self, user_id, affection_level):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "INSERT OR REPLACE INTO affection (user_id, affection_level) VALUES (?, ?)"
        cursor.execute(query, (user_id, affection_level))

        conn.commit()
        conn.close()

    def get_affection(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT affection_level FROM affection WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        conn.close()

        if result:
            return result[0]
        else:
            return 0

    def clear_affection(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "UPDATE affection SET affection_level = 0 WHERE user_id = ?"
        cursor.execute(query, (user_id,))

        conn.commit()
        conn.close()

# Below are for the chat history system whereas above are for affection system

    def save_message(self, user_id, speaker, message, max_messages=20):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "INSERT INTO chat_history (user_id, speaker, message, text_time) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (user_id, speaker, message, datetime.now()))

        delete_query = """
                       DELETE 
                       FROM chat_history
                       WHERE user_id = ? AND rowid NOT IN (SELECT rowid 
                       FROM chat_history WHERE user_id = ? 
                       ORDER BY rowid DESC LIMIT ?) 
                       """
        cursor.execute(delete_query, (user_id, user_id, max_messages))

        conn.commit()
        conn.close()
    def get_chat_history(self, user_id, limit=20):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT speaker, message FROM chat_history WHERE user_id = ? ORDER BY text_time ASC LIMIT ?"
        cursor.execute(query, (user_id, limit))
        results = cursor.fetchall()
        conn.close()
        history = []
        for speaker, message in results:
            history.append({"role": speaker, "content": message})

        return history
    def clear_chat_history(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = "DELETE FROM chat_history WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        rows_deleted = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_deleted > 0