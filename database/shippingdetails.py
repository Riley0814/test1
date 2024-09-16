from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, text
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:123456@localhost:5432/tealounge'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定義資料庫模型
class ShippingDetails(db.Model):
    __tablename__ = 'shippingdetails'
    ShippingID = db.Column(db.Integer, primary_key=True, autoincrement=False, server_default=db.text("nextval('shippingdetail_id_seq')"))
    OrderID = db.Column(db.Integer, nullable=False)
    ProductID = db.Column(db.Integer, nullable=False)
    ProductName = db.Column(db.String(100), nullable=False)
    OrderDate = db.Column(db.Date, nullable=False, default=date.today)
    UnitPrice = db.Column(db.Numeric(10, 2), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    TotalPrice = db.Column(db.Numeric(10, 2), nullable=False)
    CustomerName = db.Column(db.String(100), nullable=False)
    CustomerPhone = db.Column(db.String(10), nullable=False)
    RecipientName = db.Column(db.String(100), nullable=False)
    RecipientPhone = db.Column(db.String(10), nullable=False)
    ShippingAddress = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<ShippingDetails {self.ShippingID}>'

# 創建序列
def create_shippingdetail_sequence(target, connection, **kw):
    connection.execute(text('CREATE SEQUENCE IF NOT EXISTS shippingdetail_id_seq START 5001'))

# 在 ShippingDetails 表創建之前創建序列
event.listen(ShippingDetails.__table__, 'before_create', create_shippingdetail_sequence)

# 創建所有的表格並插入資料
def create_tables_and_data():
    with app.app_context():
        db.create_all()

        shipping_data = [
            {'OrderID': 4006, 'ProductID': 3006, 'ProductName': '精糧黑芝麻米貝果', 'UnitPrice': 145.00, 'Quantity': 3, 'TotalPrice': 435.00, 'CustomerName': '李嵐璟', 'CustomerPhone': '0929461492', 'RecipientName': '宋言語', 'RecipientPhone': '0929271943', 'ShippingAddress': '新北市板橋區溪城路32號'},
            {'OrderID': 4007, 'ProductID': 3007, 'ProductName': '千張豆腐衣(黃豆皮) | 天然手作非基改', 'UnitPrice': 155.00, 'Quantity': 1, 'TotalPrice': 155.00, 'CustomerName': '李四', 'CustomerPhone': '0915562195', 'RecipientName': '鄭佳娜', 'RecipientPhone': '0919468412', 'ShippingAddress': '新北市板橋區新府路22號'},
            {'OrderID': 4008, 'ProductID': 3008, 'ProductName': '豆紙|千張豆腐衣(黃豆皮) | 天然手作非基改', 'UnitPrice': 155.00, 'Quantity': 2, 'TotalPrice': 310.00, 'CustomerName': '胡培源', 'CustomerPhone': '0982990035', 'RecipientName': '何朋楷', 'RecipientPhone': '0982495454', 'ShippingAddress': '新北市鶯歌區鶯桃路30號'},
            {'OrderID': 4009, 'ProductID': 3009, 'ProductName': '響鈴涮涮卷', 'UnitPrice': 90.00, 'Quantity': 1, 'TotalPrice': 90.00, 'CustomerName': '林晟谷', 'CustomerPhone': '0914837867', 'RecipientName': '蕭允歡', 'RecipientPhone': '0955261486', 'ShippingAddress': '新北市土城區青雲路12號'},
            {'OrderID': 4010, 'ProductID': 3010, 'ProductName': 'Dilmah帝瑪水果茶(檸檬萊姆口味紅茶)', 'UnitPrice': 11.00, 'Quantity': 3, 'TotalPrice': 33.00, 'CustomerName': '劉七', 'CustomerPhone': '0913402094', 'RecipientName': '鄭凱立', 'RecipientPhone': '0927493909', 'ShippingAddress': '新北市板橋區光復街33號'}
        ]

        for data in shipping_data:
            shipping = ShippingDetails(
                OrderID=data['OrderID'],
                ProductID=data['ProductID'],
                ProductName=data['ProductName'],
                UnitPrice=data['UnitPrice'],
                Quantity=data['Quantity'],
                TotalPrice=data['TotalPrice'],
                CustomerName=data['CustomerName'],
                CustomerPhone=data['CustomerPhone'],
                RecipientName=data['RecipientName'],
                RecipientPhone=data['RecipientPhone'],
                ShippingAddress=data['ShippingAddress']
            )
            db.session.add(shipping)

        db.session.commit()

# 當程式碼直接執行時，創建表格並插入資料
if __name__ == '__main__':
    create_tables_and_data()
    app.run()
