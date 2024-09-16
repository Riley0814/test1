from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, Boolean
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from decimal import Decimal, InvalidOperation
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
db = SQLAlchemy()

# 訂單狀態代碼
ORDER_STATUS_PENDING = 1  # 待確定
ORDER_STATUS_PROCESSING = 2  # 處理中
ORDER_STATUS_COMPLETED = 3  # 已完成
ORDER_STATUS_CANCELLED = 4  # 已取消

# 付款狀態代碼
PAYMENT_STATUS_UNPAID = 1  # 未付款
PAYMENT_STATUS_PAID = 2  # 已付款
PAYMENT_STATUS_CANCELLED = 3  # 已取消
PAYMENT_STATUS_REFUNDED = 4  # 已退款

# 配送狀態代碼
DELIVERY_STATUS_PREPARING = 1  # 備貨中
DELIVERY_STATUS_PROCESSING = 2  # 處理中
DELIVERY_STATUS_SHIPPED = 3  # 已發貨
DELIVERY_STATUS_DELIVERED = 4  # 已送達
DELIVERY_STATUS_RETURNED = 5  # 已退回
DELIVERY_STATUS_CANCELLED = 6  # 已取消


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

class Product(db.Model):
    __tablename__ = 'products'
    ProductID = db.Column(db.Integer, primary_key=True, server_default=text("nextval('product_id_seq')"))
    ProductName = db.Column(db.String(100), nullable=False)
    Price = db.Column(db.Numeric(10, 2), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    Ingredients = db.Column(db.Text, nullable=False)
    Origin = db.Column(db.String(100), nullable=False)
    Notes = db.Column(db.Text, nullable=True)
    Status = db.Column(Boolean, nullable=False, default=False)
    is_available = db.Column(Boolean, nullable=False,default=False)
    __table_args__ = (
        db.CheckConstraint('LENGTH("ProductName") >= 2', name='check_productname_len'),
    )  
    def to_dict(self):
        return {
            'ProductID': self.ProductID,
            'ProductName': self.ProductName,
            'Price': str(self.Price),  # JSON 不支持 Decimal，需轉換為字串
            'Quantity': self.Quantity,
            'Ingredients': self.Ingredients,
            'Origin': self.Origin,
            'Notes': self.Notes,
            'Status': '上架' if self.Status else '下架',
            'is_available': '可訂購' if self.is_available else '不可訂購'
        }
def update_product_status(product_id, new_status, available_status):
    try:
        product = Product.query.get(product_id)
        if product:
            product.Status = new_status
            product.is_available = available_status
            db.session.commit()
            return True
        else:
            return False
    except Exception as e:
        db.session.rollback()
        print(f"更新商品狀態時發生錯誤: {e}")
        return False

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    ImageID = db.Column(db.Integer, primary_key=True, server_default=text("nextval('product_image_id_seq')"))
    ProductID = db.Column(db.Integer, db.ForeignKey('products.ProductID'), nullable=False)
    ImagePath = db.Column(db.String(200), nullable=False)
    ImageOrder = db.Column(db.Integer, nullable=False, default=0)

    product = db.relationship('Product', backref=db.backref('images', lazy=True))

class Register(db.Model, UserMixin):
    __tablename__ = 'register'
    MemberID = db.Column(db.Integer, primary_key=True, autoincrement=False, server_default=db.text("nextval('member_id_seq')"))
    Name = db.Column(db.String(200), nullable=False)
    Phone = db.Column(db.String(20), nullable=False, unique=True)
    Email = db.Column(db.String(250), nullable=False, unique=True)
    Password = db.Column(db.String(200), nullable=False)
    Birthday = db.Column(db.Date, nullable=False)
    LineID = db.Column(db.String(100))
    reset_token = db.Column(db.String(100), nullable=True)  # 新增的欄位

    def get_id(self):
        return str(self.MemberID)

    def is_active(self):
        return True  # 或者根據您的邏輯實現是否激活的判斷邏輯

    def __init__(self, name, phone, email, password, birthday, line_id=None):
        self.Name = name
        self.Phone = phone
        self.Email = email
        self.Password = generate_password_hash(password)
        self.Birthday = birthday
        self.LineID = line_id

    def check_password(self, password):
        return check_password_hash(self.Password, password)

    def update_profile(self, name, phone, email, birthday, password, line_id=None):
        self.Name = name
        self.Phone = phone
        self.Email = email
        self.Birthday = birthday
        self.LineID = line_id
        if password:  # 如果傳入了新密碼，則進行更新
            self.Password = generate_password_hash(password)
            
    def set_password(self, password):
        self.Password = generate_password_hash(password)


class Orders(db.Model):
    __tablename__ = 'orders'  
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=True, server_default=db.text("nextval('order_id_seq')"))
    MemberID = db.Column(db.Integer, db.ForeignKey('register.MemberID'), nullable=False)
    OrderDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    CustomerName = db.Column(db.String(100), nullable=False)
    Subtotal = db.Column(db.DECIMAL(10, 2), nullable=False)  # 新增小計欄位
    ShippingFee = db.Column(db.DECIMAL(10, 2), nullable=False, default=50.00)  # 新增運費欄位
    TotalPrice = db.Column(db.DECIMAL(10, 2), nullable=False)
    OrderStatusID = db.Column(db.Integer, nullable=True, default=ORDER_STATUS_PENDING)
    PaymentStatusID = db.Column(db.Integer, nullable=True, default=PAYMENT_STATUS_UNPAID)
    DeliveryStatusID = db.Column(db.Integer, nullable=True, default=DELIVERY_STATUS_PREPARING)
    
    order_details = db.relationship('OrderDetails', backref='order', lazy=True)

    member = db.relationship('Register', backref=db.backref('orders', lazy=True))
    
    @staticmethod
    def get_status_text(status_type, status_value):
        status_texts = {
            'OrderStatusID': {
                ORDER_STATUS_PENDING: '待確定',
                ORDER_STATUS_PROCESSING: '處理中',
                ORDER_STATUS_COMPLETED: '已完成',
                ORDER_STATUS_CANCELLED: '已取消'
            },
            'PaymentStatusID': {
                PAYMENT_STATUS_UNPAID: '未付款',
                PAYMENT_STATUS_PAID: '已付款',
                PAYMENT_STATUS_CANCELLED: '已取消',
                PAYMENT_STATUS_REFUNDED: '已退款'
            },
            'DeliveryStatusID': {
                DELIVERY_STATUS_PREPARING: '備貨中',
                DELIVERY_STATUS_PROCESSING: '處理中',
                DELIVERY_STATUS_SHIPPED: '已發貨',
                DELIVERY_STATUS_DELIVERED: '已送達',
                DELIVERY_STATUS_RETURNED: '已退回',
                DELIVERY_STATUS_CANCELLED: '已取消'
            }
        }
        
        return status_texts.get(status_type, {}).get(status_value, '未知狀態')
    
class OrderDetails(db.Model):
    __tablename__ = 'order_details'
    DetailID = db.Column(db.Integer, primary_key=True, autoincrement=True, server_default=db.text("nextval('order_detail_id_seq')"))
    OrderID = db.Column(db.Integer, db.ForeignKey('orders.OrderID'), nullable=False)
    ProductID = db.Column(db.Integer, db.ForeignKey('products.ProductID'), nullable=False)
    ProductName = db.Column(db.String(100), nullable=False)
    ProductImage = db.Column(db.String(200), nullable=True)
    UnitPrice = db.Column(db.DECIMAL(10, 2), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    TotalPrice = db.Column(db.DECIMAL(10, 2), nullable=False)
    CustomerName = db.Column(db.String(100), nullable=False)
    CustomerPhone = db.Column(db.String(10), nullable=False)
    CustomerEmail = db.Column(db.String(100), nullable=True)
    ShippingAddress = db.Column(db.String(200), nullable=False)
    ReceiverName = db.Column(db.String(100), nullable=False)
    ReceiverPhone = db.Column(db.String(10), nullable=False)
    RemittanceCode = db.Column(db.String(5), nullable=False) 

    product = db.relationship('Product', backref=db.backref('order_details', lazy=True))

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True, server_default=text("nextval('id_seq')"))
    MemberID = db.Column(db.Integer, db.ForeignKey('register.MemberID'), nullable=False)
    ProductID = db.Column(db.Integer, db.ForeignKey('products.ProductID'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
   
    # 使用 ForeignKey 參考 Register 和 Product 模型
    member = db.relationship('Register', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))
    def __repr__(self):
        return f'<CartItem {self.ProductID} for Member {self.MemberID}>'
   
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.ProductID,
            'quantity': self.quantity,
            'price': str(self.product.Price)  # JSON 不支持 Decimal，需轉換為字串
        }


