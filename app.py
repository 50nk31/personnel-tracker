from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель администратора
class User(db.Model):
    __tablename__ = 'users'  # Явное имя таблицы, чтобы не использовать ключевое слово "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Модель сотрудника
class Employee(db.Model):
    __tablename__ = 'employees'  # Явное имя таблицы
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    hours_worked = db.Column(db.Float, default=0.0)

    def get_salary(self):
        return round(self.hourly_rate * self.hours_worked, 2)

@app.route('/')
def index():
    if not User.query.first():
        # Если пользователей нет — направляем на регистрацию
        return redirect(url_for('register'))

    if 'user_id' not in session:
        return redirect(url_for('login'))

    employees = Employee.query.all()
    return render_template('index.html', employees=employees)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        return "Неверный логин или пароль"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if User.query.first():
        # Разрешена регистрация только если пользователей нет
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
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

# Временный роут для создания таблиц (зайди один раз, потом удали этот код)
@app.route('/initdb')
def initdb():
    db.create_all()
    return "Таблицы созданы"

if __name__ == '__main__':
    app.run(debug=True)
