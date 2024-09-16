from datetime import datetime
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:123456@localhost:5432/tealounge'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Orders(db.Model):
    __tablename__ = 'orders'
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=False, server_default=db.text("nextval('order_id_seq')"))
    MemberID = db.Column(db.Integer, nullable=False)
    ProductID = db.Column(db.Integer, nullable=False)
    OrderDate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ProductName = db.Column(db.String(100), nullable=False)
    CustomerName = db.Column(db.String(100), nullable=False)
    CustomerPhone = db.Column(db.String(10), nullable=False)
    CustomerEmail = db.Column(db.String(100), nullable=False)
    ShippingAddress = db.Column(db.String(200), nullable=False)
    UnitPrice = db.Column(db.DECIMAL(10, 2), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    TotalPrice = db.Column(db.DECIMAL(10, 2), nullable=False)

# 创建序列
def create_sequence(target, connection, **kw):
    connection.execute(text('CREATE SEQUENCE IF NOT EXISTS order_id_seq START 4001'))

# 在 Orders 表创建之前创建序列
from sqlalchemy import event, text
event.listen(Orders.__table__, 'before_create', create_sequence)

# 创建数据库和表
with app.app_context():
    db.create_all()

@app.route('/search', methods=['GET', 'POST'])
def search_orders():
    if request.method == 'POST':
        search_target = request.form.get('search_target')
        search_value = request.form.get('search_order')

        if search_target == 'id':
            query = Orders.query.filter_by(OrderID=search_value).all()
        elif search_target == 'phone':
            query = Orders.query.filter_by(CustomerPhone=search_value).all()
        elif search_target == 'name':
            query = Orders.query.filter_by(CustomerName=search_value).all()
        else:
            query = []

        return render_template('orders.html', orders=query)

    return render_template('search.html')

if __name__ == '__main__':
    app.run()
