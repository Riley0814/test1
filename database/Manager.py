from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:123456@localhost:5432/tealounge'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_hex(16)
db = SQLAlchemy(app)

class Manager(db.Model):
    __tablename__ = 'manager'
    Username = db.Column(db.String(50), primary_key=True)
    _password = db.Column('Password', db.String(200), nullable=False)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext_password):
        self._password = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        return check_password_hash(self._password, plaintext_password)


class Orders(db.Model):
    __tablename__ = 'orders'
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MemberID = db.Column(db.Integer, nullable=False)
    ProductID = db.Column(db.Integer, nullable=False)
    OrderDate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ProductName = db.Column(db.String(100), nullable=False)
    CustomerName = db.Column(db.String(100), nullable=False)
    CustomerPhone = db.Column(db.String(10), nullable=False)
    ShippingAddress = db.Column(db.String(200), nullable=False)
    UnitPrice = db.Column(db.DECIMAL(10, 2), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    TotalPrice = db.Column(db.DECIMAL(10, 2), nullable=False)

# 監聽事件，在建立 Orders 表前創建序列
from sqlalchemy import event, text
def create_sequence(target, connection, **kw):
    connection.execute(text('CREATE SEQUENCE IF NOT EXISTS order_id_seq START 4001'))

event.listen(Orders.__table__, 'before_create', create_sequence)

# 在應用上下文中執行的操作
with app.app_context():
    # 創建所有資料庫表
    db.create_all()

    # 檢查是否已經創建了管理員帳號，如果沒有則創建
    if not Manager.query.filter_by(Username='rcdesign03').first():
        manager = Manager(Username='rcdesign03')
        manager.password = 'stella680906'
        db.session.add(manager)
        db.session.commit()
    else:
        # 如果已經存在該管理員帳號，更新密碼
        manager = Manager.query.filter_by(Username='rcdesign03').first()
        manager.password = 'stella680906'
        db.session.commit()

    # 檢查是否已經有初始訂單資料，如果沒有則插入初始資料
    if not Orders.query.first():
        initial_orders = [
            Orders(MemberID=1001, ProductID=3001, ProductName='西班牙Spirit 洋芋片-熟成起司風味', OrderDate=datetime.now(), CustomerName='林佳', CustomerPhone='0989475982', ShippingAddress='臺北市信義區吳興街10號', UnitPrice=129.00, Quantity=1, TotalPrice=129.00),
            Orders(MemberID=1002, ProductID=3002, ProductName='西班牙Spirit 洋芋片-喜馬拉雅粉紅鹽風味', OrderDate=datetime.now(), CustomerName='向子喬', CustomerPhone='0909789027', ShippingAddress='臺北市中正區延平南路35號', UnitPrice=129.00, Quantity=2, TotalPrice=258.00),
            Orders(MemberID=1003, ProductID=3003, ProductName='鷹嘴豆零食脆片(原味)', OrderDate=datetime.now(), CustomerName='林沛羚', CustomerPhone='0963736100', ShippingAddress='臺北市士林區光華路23號', UnitPrice=109.00, Quantity=1, TotalPrice=109.00),
            Orders(MemberID=1004, ProductID=3004, ProductName='鷹嘴豆零食脆片(澳洲起司風味)', OrderDate=datetime.now(), CustomerName='盧欣彤', CustomerPhone='0976514374', ShippingAddress='臺北市士林區劍南路23號', UnitPrice=109.00, Quantity=3, TotalPrice=327.00),
            Orders(MemberID=1005, ProductID=3005, ProductName='鷹嘴豆零食脆片(番茄煙燻BBQ風味)', OrderDate=datetime.now(), CustomerName='薛欣恬', CustomerPhone='0953535735', ShippingAddress='臺北市文山區試院路1號', UnitPrice=109.00, Quantity=2, TotalPrice=218.00),
            Orders(MemberID=1006, ProductID=3006, ProductName='精糧黑芝麻米貝果', OrderDate=datetime.now(), CustomerName='李嵐璟', CustomerPhone='0929461492', ShippingAddress='台北市中正區忠孝東路一段1號', UnitPrice=145.00, Quantity=3, TotalPrice=435.00),
            Orders(MemberID=1007, ProductID=3007, ProductName='千張豆腐衣(黃豆皮) | 天然手作非基改', OrderDate=datetime.now(), CustomerName='李四', CustomerPhone='0915562195', ShippingAddress='新北市板橋區文化路一段1號', UnitPrice=155.00, Quantity=1, TotalPrice=155.00),
            Orders(MemberID=1008, ProductID=3008, ProductName='豆紙|千張豆腐衣(黃豆皮) | 天然手作非基改', OrderDate=datetime.now(), CustomerName='胡培源', CustomerPhone='0982990035', ShippingAddress='台中市南區建國南路一段1號', UnitPrice=155.00, Quantity=2, TotalPrice=310.00),
            Orders(MemberID=1009, ProductID=3009, ProductName='喜八實業香辣鳳梨煎餅', OrderDate=datetime.now(), CustomerName='何佳甄', CustomerPhone='0982990035', ShippingAddress='台北市信義區市府路45號', UnitPrice=79.00, Quantity=1, TotalPrice=79.00),
            Orders(MemberID=1010, ProductID=3010, ProductName='聖格里爾精緻可可糕點', OrderDate=datetime.now(), CustomerName='林凱傑', CustomerPhone='0985549558', ShippingAddress='台北市中正區羅斯福路4段1號', UnitPrice=250.00, Quantity=3, TotalPrice=750.00),
            Orders(MemberID=1011, ProductID=3011, ProductName='小夜燈蒜蜜碳烤糖糖地瓜', OrderDate=datetime.now(), CustomerName='簡志維', CustomerPhone='0981235909', ShippingAddress='台北市信義區光復南路360號', UnitPrice=250.00, Quantity=2, TotalPrice=500.00)
        ]

        for order in initial_orders:
            db.session.add(order)

        db.session.commit()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']
        
        manager = Manager.query.filter_by(Username=username).first()
        
        if manager:
            if manager.check_password(password):
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('orders'))
            else:
                return jsonify({'status': 'error', 'message': '用戶名或密碼錯誤'}), 401
        else:
            return jsonify({'status': 'error', 'message': '用戶名或密碼錯誤'}), 401
    
    return render_template('login.html')


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        search_target = request.form.get('search_target')
        search_value = request.form.get('search_order')
        query = []

        if search_target == 'id':
            query = Orders.query.filter(Orders.OrderID == int(search_value)).all()
        elif search_target == 'phone':
            query = Orders.query.filter(Orders.CustomerPhone.like(f'%{search_value}%')).all()
        elif search_target == 'name':
            query = Orders.query.filter(Orders.CustomerName.like(f'%{search_value}%')).all()

        return render_template('orders.html', orders=query)
    
    return render_template('orders.html')

@app.route('/api/orders', methods=['GET'])
def api_orders():
    orders = Orders.query.all()
    return jsonify([{
        'OrderID': order.OrderID,
        'OrderDate': order.OrderDate.strftime('%Y-%m-%d'),
        'CustomerName': order.CustomerName,
        'TotalPrice': float(order.TotalPrice)
    } for order in orders])

@app.route('/search_orders', methods=['POST'])
def search_orders():
    data = request.get_json()
    target = data['target']
    value = data['value']
    
    if target == 'id':
        orders = Orders.query.filter_by(OrderID=int(value)).all()
    elif target == 'phone':
        orders = Orders.query.filter(Orders.CustomerPhone.like(f'%{value}%')).all()
    elif target == 'name':
        orders = Orders.query.filter(Orders.CustomerName.like(f'%{value}%')).all()
    else:
        orders = []
    
    orders_list = []
    for order in orders:
        order_dict = {
            'OrderID': order.OrderID,
            'OrderDate': order.OrderDate.strftime('%Y-%m-%d'),
            'CustomerName': order.CustomerName,
            'TotalPrice': float(order.TotalPrice)
        }
        orders_list.append(order_dict)
    
    return jsonify(orders_list)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
