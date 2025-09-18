import sqlite3

# подключение к базе
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# список предметов в нужном порядке
subjects = [
    'Математика',
    'Физика',
    'Русский язык',
    'История',
    'Английский язык',
    'Биология',
    'Литература'
]

# добавляем предметы, если их еще нет
for index, subject in enumerate(subjects, start=1):
    cursor.execute("INSERT OR IGNORE INTO subjects (id, name) VALUES (?, ?)", (index, subject))

conn.commit()
conn.close()

print("Предметы добавлены и зафиксированы.")
