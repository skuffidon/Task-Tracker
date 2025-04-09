import os
from datetime import datetime, date
from flask import Flask, request, redirect, url_for, flash, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

# Создаем папку для загрузок, если её нет
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'very-secret-key'  # Замените на более надежный ключ
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carinfo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Модель данных
class CarInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_number = db.Column(db.String(20), nullable=False)
    owner_name = db.Column(db.String(50), nullable=False)
    car_brand = db.Column(db.String(50))
    customer_name = db.Column(db.String(50))
    # Хранение даты заказа в формате Date (рекомендуется вводить дату в формате YYYY-MM-DD)
    order_date = db.Column(db.Date, nullable=True)
    photo_filename = db.Column(db.String(100))  # имя файла фотографии

    def __repr__(self):
        return f'<CarInfo {self.car_number} - {self.order_date}>'

# Простая проверка аутентификации
def is_logged_in():
    return session.get('logged_in') is True

# Кастомная реализация админ-панели с защитой
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not is_logged_in():
            return redirect(url_for('login'))
        return super(MyAdminIndexView, self).index()

    def is_accessible(self):
        return is_logged_in()

class MyModelView(ModelView):
    # Устанавливаем сортировку по убыванию по полю order_date (True = DESC)
    column_default_sort = ('order_date', True)

    def is_accessible(self):
        return is_logged_in()

# Настройка админ-панели
admin = Admin(app, name='CarInfo Admin', template_mode='bootstrap3',
              index_view=MyAdminIndexView())
admin.add_view(MyModelView(CarInfo, db.session))

# Маршруты для аутентификации
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Простейшая проверка: установите свои значения
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            flash("Вы успешно вошли в систему.", "success")
            return redirect(url_for('admin.index'))
        else:
            error = "Неверный логин или пароль."
    return render_template_string('''
    <!doctype html>
    <html lang="ru">
      <head>
        <meta charset="utf-8">
        <title>Вход в админ-панель</title>
      </head>
      <body>
        <h2>Вход в админ-панель</h2>
        {% if error %}
            <p style="color: red;">{{ error }}</p>
        {% endif %}
        <form method="post">
          <label>Логин:</label><br>
          <input type="text" name="username"><br>
          <label>Пароль:</label><br>
          <input type="password" name="password"><br><br>
          <input type="submit" value="Войти">
        </form>
      </body>
    </html>
    ''', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("Вы вышли из системы.", "info")
    return redirect(url_for('login'))

# Если требуется добавить возможность загрузки фотографии через отдельный endpoint,
# можно реализовать его здесь. В данном примере загрузка осуществляется через админ-панель.
# Но если потребуется отдельная форма для загрузки фото (администратором), добавьте маршрут.

# Запуск приложения
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Для разработки: запуск через app.run; в продакшене используйте Gunicorn и настройку Nginx
    app.run(host='0.0.0.0', port=5000, debug=True)
