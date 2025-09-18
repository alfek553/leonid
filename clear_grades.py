import sqlite3

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def clear_grades_and_subjects():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM grades")
    cursor.execute("DELETE FROM subjects")

    conn.commit()
    conn.close()
    print("Оценки и предметы удалены.")
    print("Для добавления новых, сначала добавить предметы")

if __name__ == '__main__':
    clear_grades_and_subjects()
