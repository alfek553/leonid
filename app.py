from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = 'database.db'

# 1. Фиксированный порядок предметов (замените на свои названия и id)
SUBJECTS_ORDER = []

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# 2. Загружаем список предметов один раз при запуске
def load_subjects_order():
    global SUBJECTS_ORDER
    conn = get_db_connection()
    cursor = conn.cursor()
    # Убедитесь, что у вас есть эти предметы в таблице subjects с правильными id
    cursor.execute("SELECT id, name FROM subjects ORDER BY id")
    SUBJECTS_ORDER = cursor.fetchall()
    conn.close()

load_subjects_order()

# 3. Стартовая страница - логин
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['login']
        password_input = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE login = ? AND password = ?', (login_input, password_input))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            if user['role'] == 'student':
                return redirect(url_for('student'))
            else:
                return redirect(url_for('teacher'))
        else:
            return render_template('login.html', error='Неверный логин или пароль')
    return render_template('login.html', error=None)

# 4. Страница ученика
@app.route('/student')
def student():
    if 'user_id' in session and session['role'] == 'student':
        months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
        
        month = request.args.get('month')
        if month is None:
            month = months[datetime.now().month - 1]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT subjects.name, grades.month, grades.grade
            FROM grades
            JOIN subjects ON grades.subject_id = subjects.id
            WHERE grades.user_id = ? AND grades.month = ?
        ''', (session['user_id'], month))
        grades = cursor.fetchall()
        conn.close()

        return render_template('student.html', grades=grades, months=months, selected_month=month)
    return redirect(url_for('login'))

# 5. Страница учителя (выбор студента и оценки)
@app.route('/teacher')
def teacher():
    if 'user_id' in session and session['role'] == 'teacher':
        student_id = request.args.get('student_id', type=int)
        month = request.args.get('month')
    if 'user_id' in session and session['role'] == 'teacher':
        month = request.args.get('month')
        months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

        if month is None:
            month = months[0]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем список всех предметов в фиксированном порядке
        subjects = SUBJECTS_ORDER

        # Получаем список студентов в группе (замените на свою логику)
        cursor.execute('''
            SELECT id, login, first_name, last_name
            FROM users
            WHERE group_id = (SELECT group_id FROM users WHERE id = ?) AND role = 'student'
        ''', (session['user_id'],))
        students_list = cursor.fetchall()

        # Выбираем текущего студента
        if student_id is None and students_list:
            student_id = students_list[0]['id']
        elif student_id is None:
            return render_template('teacher.html', students={}, students_list=students_list, current_student=None, months=months, selected_month=month)

        # Получаем оценки выбранного студента за месяц
        cursor.execute('''
            SELECT users.id, users.login, users.first_name, users.last_name,
                   subjects.id as subject_id, subjects.name, grades.month, grades.grade
            FROM users
            JOIN grades ON users.id = grades.user_id
            JOIN subjects ON grades.subject_id = subjects.id
            WHERE users.id = ? AND grades.month = ?
        ''', (student_id, month))
        grades = cursor.fetchall()

        # Создаем словарь студентов
        students = {}
        for s in students_list:
            students[s['id']] = {
                'id': s['id'],
                'login': s['login'],
                'first_name': s['first_name'],
                'last_name': s['last_name'],
                'grades': []
            }

        # Создаем словарь оценок по предметам
        grades_dict = {g['subject_id']: g['grade'] for g in grades}

        # Вписываем оценки в порядке SUBJECTS_ORDER
        for subject in subjects:
            subject_id = subject['id']
            grade_value = grades_dict.get(subject_id, None)
            students[student_id]['grades'].append({
                'subject_name': subject['name'],
                'subject_id': subject_id,
                'month': month,
                'grade': grade_value
            })

        return render_template('teacher.html', students=students, students_list=students_list, current_student=int(student_id), months=months, selected_month=month)

    return redirect(url_for('login'))

# 6. Маршруты редактирования и обновления оценок
@app.route('/edit_grade/<int:user_id>/<int:subject_id>/<string:month>', methods=['GET'])
def edit_grade(user_id, subject_id, month):
    if 'user_id' in session and session['role'] == 'teacher':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT users.login, subjects.name, grades.month, grades.grade
            FROM grades
            JOIN users ON grades.user_id = users.id
            JOIN subjects ON grades.subject_id = subjects.id
            WHERE grades.user_id = ? AND grades.subject_id = ? AND grades.month = ?
        ''', (user_id, subject_id, month))
        grade = cursor.fetchone()
        conn.close()

        if grade:
            return render_template('edit_grade.html', grade=grade, user_id=user_id, subject_id=subject_id, month=month, student_id=user_id)
        return "Оценка не найдена"
    return redirect(url_for('login'))

@app.route('/update_grade/<int:user_id>/<int:subject_id>/<string:month>', methods=['POST'])
def update_grade(user_id, subject_id, month):
    if 'user_id' in session and session['role'] == 'teacher':
        try:
            new_grade = int(request.form['grade'])
        except ValueError:
            return "Некорректная оценка"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE grades
            SET grade = ?
            WHERE user_id = ? AND subject_id = ? AND month = ?
        ''', (new_grade, user_id, subject_id, month))
        conn.commit()
        conn.close()

        return redirect(url_for('teacher', student_id=user_id))
    return redirect(url_for('login'))

# 7. Выход
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('login'))
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)