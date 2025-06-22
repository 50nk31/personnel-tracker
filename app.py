from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL") or 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    hours_worked = db.Column(db.Float, default=0.0)

    def get_salary(self):
        return round(self.hourly_rate * self.hours_worked, 2)

@app.route('/initdb')
def initdb():
    db.create_all()
    return "База данных и таблицы созданы"

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Фейковый логин: любой логин и пароль пускают
        username = request.form['username']
        if not username:
            return render_template('login.html', error="Введите имя пользователя")

        # Создаём/находим пользователя в базе (чтобы потом можно было выйти)
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()

        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    employees = Employee.query.all()
    return render_template('index.html', employees=employees)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add_employee():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    name = request.form['name']
    hourly_rate = float(request.form['hourly_rate'])
    hours_worked = float(request.form['hours_worked'])
    employee = Employee(name=name, hourly_rate=hourly_rate, hours_worked=hours_worked)
    db.session.add(employee)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_employee(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
