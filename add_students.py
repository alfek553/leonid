import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Добавляем 26 новых студентов
for i in range(2, 28):  # Начинаем с 2, так как student1 уже есть
    login = f'student{i}'
    password = f'password{i}'
    cursor.execute("INSERT INTO users (login, password, role, group_id) VALUES (?, ?, 'student', 1)", (login, password))

conn.commit()
conn.close()

print("26 новых студентов добавлены в базу данных.")
