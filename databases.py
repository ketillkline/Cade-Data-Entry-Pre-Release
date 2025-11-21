import sqlite3

class DatabaseManager:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connection = sqlite3.connect(f'{self.db_name}.db')

        self.cursor = self.connection.cursor()
        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS "{self.db_name}"(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL)
        ''')
        self.connection.commit()

    def insert_entry(self, text: str):
        self.cursor.execute(f'''
        INSERT INTO {self.db_name} (text) VALUES (?)''', (text,))
        self.connection.commit()

    def delete_entry(self, id: int):
        self.cursor.execute(f'''
        DELETE FROM {self.db_name} WHERE id = ?''', (id,))
        self.connection.commit()

    def fetch_entries(self):
        self.cursor.execute(f'''
        SELECT text FROM {self.db_name}
        ''')
        return self.cursor.fetchall()

    def clear_entries(self):
        self.cursor.execute(f'''
        DELETE FROM {self.db_name}
        ''')
        names = self.cursor.execute("SELECT name FROM sqlite_sequence").fetchall()
        self.cursor.execute(f"""DELETE FROM sqlite_sequence WHERE name = '{self.db_name}'""")
        self.connection.commit()

    def id_from_text(self, text: str): # returns tuple (id,)
        self.cursor.execute(f'''
        SELECT id FROM {self.db_name} WHERE text = ?''', (text,))
        return self.cursor.fetchone()


