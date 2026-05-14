from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(100))

    role = db.Column(db.String(20))


class Quiz(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    category = db.Column(db.String(100))


class Question(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    quiz_id = db.Column(db.Integer)

    question = db.Column(db.String(500))

    option1 = db.Column(db.String(200))

    option2 = db.Column(db.String(200))

    option3 = db.Column(db.String(200))

    option4 = db.Column(db.String(200))

    answer = db.Column(db.String(200))


class Score(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))

    quiz = db.Column(db.String(100))

    score = db.Column(db.Integer)

@app.route('/')
def home():

    quizzes = Quiz.query.all()

    return render_template(
        'index.html',
        quizzes=quizzes
    )


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            return "Username already exists"

        user = User(
            username=username,
            password=password,
            role="student"
        )

        db.session.add(user)

        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    error = ""

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session['username'] = user.username

            session['role'] = user.role

            if user.role == "admin":

                return redirect('/admin')

            else:

                return redirect('/dashboard')

        else:

            error = "Invalid Username or Password"

    return render_template(
        'login.html',
        error=error
    )


@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


@app.route('/dashboard')
def dashboard():

    if 'username' not in session:

        return redirect('/login')

    quizzes = Quiz.query.all()

    return render_template(
        'dashboard.html',
        quizzes=quizzes,
        username=session['username']
    )



@app.route('/admin')
def admin():

    if 'username' not in session:

        return redirect('/login')

    if session['role'] != 'admin':

        return "Access Denied"

    quizzes = Quiz.query.all()

    questions = Question.query.all()

    scores = Score.query.all()

    return render_template(
        'admin_dashboard.html',
        quizzes=quizzes,
        questions=questions,
        scores=scores,
        username=session['username']
    )


@app.route('/create_quiz', methods=['POST'])
def create_quiz():

    if session['role'] != 'admin':

        return "Access Denied"

    category = request.form['category']

    quiz = Quiz(category=category)

    db.session.add(quiz)

    db.session.commit()

    return redirect('/admin')

@app.route('/add_question', methods=['POST'])
def add_question():

    if session['role'] != 'admin':

        return "Access Denied"

    question = Question(

        quiz_id=request.form['quiz_id'],

        question=request.form['question'],

        option1=request.form['option1'],

        option2=request.form['option2'],

        option3=request.form['option3'],

        option4=request.form['option4'],

        answer=request.form['answer']
    )

    db.session.add(question)

    db.session.commit()

    return redirect('/admin')


@app.route('/delete_question/<int:id>')
def delete_question(id):

    if session['role'] != 'admin':

        return "Access Denied"

    question = Question.query.get(id)

    db.session.delete(question)

    db.session.commit()

    return redirect('/admin')


@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def quiz(quiz_id):

    if 'username' not in session:

        return redirect('/login')

    quiz = Quiz.query.get(quiz_id)

    questions = Question.query.filter_by(
        quiz_id=quiz_id
    ).all()

    if request.method == 'POST':

        marks = 0

        for q in questions:

            selected = request.form.get(str(q.id))

            if selected == q.answer:

                marks += 1

        result = Score(

            username=session['username'],

            quiz=quiz.category,

            score=marks
        )

        db.session.add(result)

        db.session.commit()

        return render_template(
            'result.html',
            score=marks,
            total=len(questions),
            questions=questions,
            username=session['username']
        )

    return render_template(
        'attempt_quiz.html',
        quiz=quiz,
        questions=questions,
        username=session['username']
    )



with app.app_context():

    db.create_all()

    admin = User.query.filter_by(
        username='admin'
    ).first()

    if not admin:

        admin_user = User(
            username='admin',
            password='admin123',
            role='admin'
        )

        db.session.add(admin_user)

        db.session.commit()

if __name__ == '__main__':

    app.run()