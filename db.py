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
              user_id TEXT,
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