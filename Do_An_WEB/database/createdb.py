import sqlite3

conn = sqlite3.connect('database/data.db')

c = conn.cursor()

c.execute("""
        CREATE TABLE login (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT
          )
""")

conn.commit()
conn.close()