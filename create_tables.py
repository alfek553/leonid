import sqlite3

DATABASE = 'database.db'

def create_tables():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            user_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            grade INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            PRIMARY KEY (user_id, subject_id, month)
        )
    ''')

    conn.commit()
    conn.close()
    print("Таблицы subjects и grades созданы.")

if __name__ == '__main__':
    create_tables()
