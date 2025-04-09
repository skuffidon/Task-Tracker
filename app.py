from flask import Flask, request, redirect, url_for, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os

# Создаем папку для загрузок, если её нет
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carinfo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Определяем модель данных
class CarInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_number = db.Column(db.String(20), nullable=False)
    owner_name = db.Column(db.String(50), nullable=False)
    car_brand = db.Column(db.String(50))
    customer_name = db.Column(db.String(50))
    order_date = db.Column(db.String(20))
    photo_filename = db.Column(db.String(100))  # имя файла фотографии

    def __repr__(self):
        return f'<CarInfo {self.car_number}>'

# Настраиваем админ-панель через Flask-Admin
admin = Admin(app, name='CarInfo Admin', template_mode='bootstrap3')
admin.add_view(ModelView(CarInfo, db.session))

# Главная страница для приема данных (без графики, пример формы)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        car_number = request.form['car_number']
        owner_name = request.form['owner_name']
        car_brand = request.form.get('car_brand', '')
        customer_name = request.form.get('customer_name', '')
        order_date = request.form.get('order_date', '')

        # Обработка файла (фотографии)
        file = request.files.get('photo')
        filename = None
        if file and file.filename:
            filename = file.filename  # В реальном приложении стоит генерировать уникальное имя
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        carinfo = CarInfo(
            car_number=car_number,
            owner_name=owner_name,
            car_brand=car_brand,
            customer_name=customer_name,
            order_date=order_date,
            photo_filename=filename
        )
        db.session.add(carinfo)
        db.session.commit()
        flash("Данные успешно сохранены.", "success")
        return redirect(url_for('index'))

    # Простая HTML-форма (для тестового ввода)
    html = """
    <!doctype html>
    <html lang="ru">
      <head>
        <meta charset="utf-8">
        <title>Загрузка данных</title>
      </head>
      <body>
        <h1>Загрузить информацию о заказе</h1>
        <form method="post" enctype="multipart/form-data">
          <label>Номер автомобиля:</label><br>
          <input type="text" name="car_number"><br>
          <label>Владелец:</label><br>
          <input type="text" name="owner_name"><br>
          <label>Марка:</label><br>
          <input type="text" name="car_brand"><br>
          <label>ФИО заказчика:</label><br>
          <input type="text" name="customer_name"><br>
          <label>Дата заказа:</label><br>
          <input type="text" name="order_date"><br>
          <label>Фото (файл):</label><br>
          <input type="file" name="photo"><br><br>
          <button type="submit">Отправить данные</button>
        </form>
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            <ul>
            {% for category, message in messages %}
              <li>{{ message }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        <p><a href="/admin/">Перейти в админ-панель</a></p>
      </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # В режиме разработки, для продакшена запуск через Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)
