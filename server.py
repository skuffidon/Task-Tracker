from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Используем SQLite для простоты; в продакшене можно выбрать другую СУБД
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carinfo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Определяем модель данных, соответствующую CarInfo
class CarInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_number = db.Column(db.String(20), nullable=False)
    owner_name = db.Column(db.String(50), nullable=False)
    car_brand = db.Column(db.String(50))
    customer_name = db.Column(db.String(50))
    order_date = db.Column(db.String(20))
    photo_before = db.Column(db.String(200))
    photo_during = db.Column(db.String(200))
    photo_after = db.Column(db.String(200))

@app.route('/api/carinfo/upload', methods=['POST'])
def upload_car_info():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    car_info = CarInfo(
        car_number=data.get('carNumber'),
        owner_name=data.get('ownerName'),
        car_brand=data.get('carBrand'),
        customer_name=data.get('customerName'),
        order_date=data.get('orderDate'),
        photo_before=data.get('photoBefore'),
        photo_during=data.get('photoDuring'),
        photo_after=data.get('photoAfter')
    )
    db.session.add(car_info)
    db.session.commit()
    return jsonify({'message': 'Data uploaded successfully'}), 200

if name == '__main__':
    # При первом запуске создадим базу данных
    db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)