import sqlite3

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def add_all_subjects_grades():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Названия месяцев
    months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
              'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

    # Получаем все предметы
    cursor.execute("SELECT id, name FROM subjects")
    subjects = cursor.fetchall()

    # Получаем всех студентов
    cursor.execute("SELECT id FROM users WHERE role='student'")
    students = cursor.fetchall()

    for student in students:
        user_id = student['id']
        for month in months:
            for subject in subjects:
                # Проверка, есть ли уже оценка для этого студента, предмета и месяца
                cursor.execute('''
                    SELECT 1 FROM grades WHERE user_id=? AND subject_id=? AND month=?
                ''', (user_id, subject['id'], month))
                if cursor.fetchone() is None:
                    # Заполняем пустыми оценками
                    grade_value = 0
                    cursor.execute('''
                        INSERT INTO grades (user_id, subject_id, month, grade)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, subject['id'], month, grade_value))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_all_subjects_grades()

