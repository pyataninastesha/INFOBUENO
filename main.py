from flask import Flask, render_template, redirect, flash, url_for, request, jsonify, send_from_directory
from flask import session as flask_session
from db_session import global_init, create_session
from models.user import User
from models.subject import Subject  # Модель предметов
from models.topic import Topic  # Модель тем
from models.question import Question  # Модель вопросов
from models.test import Test  # Модель тестов
from forms.forms import RegistrationForm, LoginForm
import random
import os
import base64


app = Flask(__name__)
app.secret_key = "secret_key"

# инициализация базы данных
global_init("db/database.db")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        session = create_session()
        existing_user = session.query(User).filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        if existing_user:
            flash('Пользователь с таким именем или email уже существует.')
            return redirect('/register')

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        session.add(new_user)
        session.commit()
        flash('Вы успешно зарегистрировались!')
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        session = create_session()
        user = session.query(User).filter(User.email == email, User.password == password).first()
        if not user:
            flash('Неверный email или пароль.')
            return redirect(url_for('login'))

        flask_session['user_id'] = user.id
        flash('Вы успешно вошли в систему!')
        return redirect(url_for('dashboard', username=user.username))

    return render_template('login.html', form=form)


@app.route('/dashboard/<username>')
def dashboard(username):
    session = create_session()
    subjects = session.query(Subject).all()  # Получаем все предметы
    return render_template('dashboard.html', username=username, subjects=subjects)


@app.route('/api/subjects')
def get_subjects():
    """Возвращает список всех предметов."""
    session = create_session()
    subjects = session.query(Subject).all()

    if not subjects:
        return jsonify([])

    subjects_data = [{"id": subject.id, "name": subject.name} for subject in subjects]
    return jsonify(subjects_data)


@app.route('/api/topics')
def get_topics():
    subject_id = request.args.get('subject_id', type=int)
    session = create_session()
    topics = session.query(Topic).filter(Topic.subject_id == subject_id).all()

    if not topics:
        return jsonify([])

    topics_data = [{"id": topic.id, "name": topic.name} for topic in topics]
    return jsonify(topics_data)


@app.route('/api/questions')
def get_questions():
    try:
        subject_id = request.args.get('subject_id', type=int)
        topic_id = request.args.get('topic_id', type=int)

        if not subject_id or not topic_id:
            return jsonify({"error": "subject_id and topic_id are required"}), 400

        session = create_session()
        questions = session.query(Question).filter(
            Question.topic_id == topic_id,
            Topic.subject_id == subject_id
        ).join(Topic).all()

        questions_data = []
        for q in questions:
            task_data = None
            task_type = q.task_type

            if task_type == 'text':
                task_data = q.task.decode('utf-8') if isinstance(q.task, bytes) else q.task
            elif task_type == 'image':
                if q.task_blob:
                    task_data = base64.b64encode(q.task_blob).decode('utf-8')

            answer_data = q.answer.decode('utf-8') if isinstance(q.answer, bytes) else q.answer

            questions_data.append({
                "id": q.id,
                "task": task_data,
                "task_type": task_type,
                "answer": answer_data
            })

        return jsonify(questions_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/test', methods=['GET'])
def generate_test():
    subject_id = request.args.get('subject_id', type=int)
    topic_id = request.args.get('topic_id', type=int)
    session = create_session()
    topic = session.query(Topic).get(topic_id)
    if not topic:
        return jsonify({"error": "Тема не найдена"}), 404
    questions = session.query(Question).filter(Question.topic_id == topic_id).all()
    if not questions:
        return jsonify({"error": "Нет вопросов для данной темы"}), 404
    random_questions = random.sample(questions, min(len(questions), 5))  # генерация 5 случайных вопросов

    questions_data = []
    for q in random_questions:
        task_data = None
        if q.task_type == 'text':
            task_data = q.task.decode('utf-8') if isinstance(q.task, bytes) else q.task
        elif q.task_type == 'image' and q.task_blob:
            task_data = base64.b64encode(q.task_blob).decode('utf-8')  # перекодировка изображений

        questions_data.append({
            "id": q.id,
            "task": task_data,
            "task_type": q.task_type,
        })

    return jsonify({"topicName": topic.name, "questions": questions_data})


@app.route('/api/submit_test', methods=['POST'])
def submit_test():
    data = request.json
    answers = data.get('answers', {})
    topic_id = data.get('topicId')
    subject_id = data.get('subjectId')
    user_id = 1

    session = create_session()
    questions = session.query(Question).filter(Question.id.in_(answers.keys())).all()
    correct_count = 0
    results = []

    for question in questions:
        user_answer = answers.get(str(question.id), "").strip().lower()
        is_correct = user_answer == question.answer.strip().lower()
        if is_correct:
            correct_count += 1
        results.append({
            "questionId": question.id,
            "isCorrect": is_correct,
            "userAnswer": user_answer,
            "correctAnswer": question.answer.strip().lower()
        })

    # запись результата тестов в базу данных
    test_result = Test(user_id=user_id, topic_id=topic_id, score=correct_count)
    session.add(test_result)
    session.commit()

    return jsonify({
        "correctCount": correct_count,
        "totalQuestions": len(questions),
        "results": results
    })


@app.route('/api/user', methods=['GET'])
def get_user():
    user_id = flask_session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    try:
        db_session = create_session()

        user_id = int(user_id)

        user = db_session.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = {"id": user.id, "username": user.username}
        return jsonify(user_data)

    except ValueError:
        return jsonify({"error": "Invalid user_id format"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/tests', methods=['GET'])
def get_tests():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        user_id = int(user_id)
        session = create_session()

        tests = session.query(Test).join(Topic).filter(Test.user_id == user_id).all()

        test_data = [
            {"test_name": test.topic.name, "result": test.score}
            for test in tests
        ]
        return jsonify(test_data)

    except ValueError:
        return jsonify({"error": "Invalid user_id format"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory("static/images", filename)


@app.route('/logout', methods=['POST'])
def logout():
    flask_session.clear()  # очистка сессии для выхода
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5008)))