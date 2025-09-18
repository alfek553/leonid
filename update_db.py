import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("ALTER TABLE users ADD COLUMN first_name TEXT")
cursor.execute("ALTER TABLE users ADD COLUMN last_name TEXT")

conn.commit()
conn.close()
