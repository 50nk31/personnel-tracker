from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///test.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель сотрудника
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    hours_worked = db.Column(db.Float, default=0.0)

    def get_salary(self):
        return round(self.hourly_rate * self.hours_worked, 2)

# Создать таблицы
@app.route('/initdb')
def initdb():
    db.create_all()
    return "База данных и таблицы созданы"

# Главная страница с отображением сотрудников
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    employees = Employee.query.all()
    return render_template('index.html', employees=employees)

# Логин
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user_id'] = 1
        return redirect(url_for('index'))
    return render_template('login.html')

# Выход (logout)
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Добавить сотрудника
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

# Удалить сотрудника
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
