from datetime import datetime, timedelta
import os
import secrets
from flask import Flask, request, render_template, redirect, url_for, session, jsonify, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from sqlalchemy import text, Boolean
from sqlalchemy.exc import IntegrityError
from wtforms import StringField, PasswordField, SubmitField, DateField, FloatField, IntegerField, DecimalField, BooleanField
from wtforms.validators import DataRequired, InputRequired, Email, Length, EqualTo
from flask_wtf import FlaskForm
from itertools import groupby
from model import db, Manager, Product, ProductImage, Register, Orders, OrderDetails, CartItem
from decimal import Decimal

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

# 確保你的 UPLOAD_FOLDER 和靜態路徑設定正確
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:CQ3CvCTEkRzvYyTSQgZoW5gmkkr4yyqP@dpg-cr2po3ij1k6c73ebmgbg-a.singapore-postgres.render.com:5432/tea_lounge'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_ECHO'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # 使用 Gmail 的 SMTP 伺服器
app.config['MAIL_PORT'] = 587  # 使用 Gmail 的 SMTP 端口
app.config['MAIL_USE_TLS'] = True  # Gmail 支持 TLS 加密
app.config['MAIL_USERNAME'] = 'oce24680@gmail.com'  # 你的 Gmail 帳號
app.config['MAIL_PASSWORD'] = 'nnqe wowc fppp ltxi'  # 你的 Gmail 密碼
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@gmail.com'  # 默認的發件人地址

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
mail = Mail(app)

# Ensure model import is done after app is initialized
from model import db, Manager, Product, ProductImage, Register, Orders, OrderDetails, CartItem

    
class User(UserMixin):
    def __init__(self, id, name=None, phone=None, email=None):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email

    @staticmethod
    def get(id):
        return Register.query.get(id)  # 確保這裡查找的是 Register 的 ID

    def get_id(self):
        return str(self.id)  # 返回字符串形式的 id

@login_manager.user_loader
def load_user(user_id):
    # 根據 user_id 查詢 Register 模型
    user = Register.query.get(int(user_id))
    if user is None:
        return None
   
    # 創建 User 實例，並傳遞其他用戶資料（如需要）
    return User(id=user.MemberID, name=user.Name, phone=user.Phone, email=user.Email)

def send_reset_email(user):
    token = user.reset_token
    msg = Message('重設您的 Tea Lounge 密碼',
                  sender='noreply@yourdomain.com',
                  recipients=[user.Email])
    msg.body = f'''要重設您的密碼，請點擊以下連結：
{url_for('reset_password', token=token, _external=True)}

如果您沒有要求重設密碼，請忽略此郵件。
'''
    mail.send(msg)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS  

class ProductForm(FlaskForm):
    ProductName = StringField('產品名稱', validators=[DataRequired()])
    Quantity = IntegerField('數量', validators=[DataRequired()])
    Price = DecimalField('價格', validators=[DataRequired()], places=2)
    Ingredients = StringField('成分')
    Origin = StringField('產地')
    Notes = StringField('備註')
    submit = SubmitField('提交')
    
    
def update_order_status(order_id, new_order_status, new_payment_status, new_delivery_status):
    try:
        order = Orders.query.get(order_id)
        if order:
            order.OrderStatusID = new_order_status
            order.PaymentStatusID = new_payment_status
            order.DeliveryStatusID = new_delivery_status
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新訂單狀態時發生錯誤: {e}")
        return False

def get_product_id(product_name):
    try:
        product = Product.query.filter_by(ProductName=product_name).first()
        if product:
            return product.ProductID
        else:
            app.logger.info(f"未找到產品: {product_name}")
            return None
    except Exception as e:
        app.logger.error(f"查詢產品 ID 時發生錯誤: {e}")
        return None

def get_member_id(email):
    try:
        result = db.session.execute(text("SELECT MemberID FROM register WHERE Email = :email"), {'email': email})
        member = result.fetchone()
        return member[0] if member else None
    except Exception as e:
        print(f"查詢會員 ID 時發生錯誤: {e}")
        return None

def insert_order_details(order_id, product_name, product_image, unit_price, quantity, total_price, customer_name, customer_phone, customer_email, shipping_address, receiver_name, receiver_phone, remittance_code):
    try:
        product_id = get_product_id(product_name)
        member_id = get_member_id(customer_email)
        
        if product_id and member_id:
            order_detail = OrderDetails(
                OrderID=order_id,
                ProductID=product_id,
                ProductName=product_name,
                ProductImage=product_image,
                UnitPrice=unit_price,
                Quantity=quantity,
                TotalPrice=total_price,
                CustomerName=customer_name,
                CustomerPhone=customer_phone,
                CustomerEmail=customer_email,
                ShippingAddress=shipping_address,
                ReceiverName=receiver_name,
                ReceiverPhone=receiver_phone,
                RemittanceCode=remittance_code
            )
            db.session.add(order_detail)
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"插入訂單明細時發生錯誤: {e}")
        return False
    
def get_cart_items(member_id):
    cart_items = CartItem.query.filter_by(MemberID=member_id).all()
    items = []
    for cart_item in cart_items:
        items.append({
            'product': {
                'ProductID': cart_item.product.ProductID,
                'ProductName': cart_item.product.ProductName,
                'Price': cart_item.product.Price
            },
            'quantity': cart_item.quantity
        })
    return items

def calculate_subtotal(member_id):
    cart_items = get_cart_items(member_id)  # 獲取購物車中的項目
    subtotal = sum(
        Decimal(item['product']['Price']) * item['quantity']
        for item in cart_items
    )
    return subtotal

def calculate_shipping_fee():
    # 假設運費是固定的，你可以根據需要進行調整
    return Decimal('50.00')  # 例如：固定運費50元

class RegisterForm(FlaskForm):
    name = StringField('姓名', validators=[InputRequired(), Length(max=200)])
    phone = StringField('電話', validators=[InputRequired(), Length(max=20)])
    email = StringField('電子郵件', validators=[InputRequired(), Email(), Length(max=250)])
    password = PasswordField('密碼', validators=[InputRequired(), Length(min=6)])
    pass_confirm = PasswordField('確認密碼', validators=[InputRequired(), EqualTo('password', message='密碼必須相符')])
    birthday = DateField('生日', format='%Y-%m-%d', validators=[InputRequired()])
    submit = SubmitField('註冊')

class LoginForm(FlaskForm):
    phone = StringField('電話', validators=[InputRequired(), Length(max=20)])
    password = PasswordField('密碼', validators=[InputRequired()])
    submit = SubmitField('登入')
    
@app.route('/manager')
def login_redirect():
    return redirect(url_for('manager_login'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('沒有選擇檔案', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('沒有選擇檔案', 'error')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('檔案上傳成功', 'success')
        return redirect(url_for('uploaded_file', filename=filename))
    
    flash('檔案格式不允許', 'error')
    return redirect(request.url)

@app.route('/uploaded/<filename>')
def uploaded_file(filename):
    return redirect(url_for('static', filename=f'uploads/{filename}'))

@app.route('/manager_login', methods=['GET', 'POST'])
def manager_login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            manager = Manager.query.filter_by(Username=username).first()
            
            if manager and manager.check_password(password):
                session['logged_in'] = True
                session['username'] = username
                next_url = request.args.get('next')  # 確保處理 next 參數
                return redirect(next_url or url_for('orders'))
            
            return jsonify({'status': 'error', 'message': '用戶名或密碼錯誤'}), 401
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    return render_template('login.html')


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['ProductName']
        quantity = request.form['Quantity']
        price = request.form['Price']
        ingredients = request.form['Ingredients']
        origin = request.form['Origin']
        notes = request.form['Notes']
        images = request.files.getlist('images')

        # 處理數量
        quantity = process_quantity(quantity)
        if quantity is None:
            flash('數量必須是有效的數字。', 'error')
            return redirect(url_for('add_product'))

        # 處理價格
        price = process_price(price)
        if price is None:
            flash('價格必須是有效的數字。', 'error')
            return redirect(url_for('add_product'))

        # 檢查產品是否存在
        product_id = handle_product(name, quantity, price, ingredients, origin, notes)
        if product_id is None:
            return redirect(url_for('add_product'))

        # 處理產品圖片
        handle_images(images, product_id)

        flash('產品已新增或更新。', 'success')
        return redirect(url_for('add_product'))

    return render_template('add_product.html')

def process_quantity(quantity):
    if quantity.strip():
        try:
            return int(quantity)
        except ValueError:
            return None
    return None

def process_price(price):
    try:
        return round(float(price), 2)
    except ValueError:
        return None

def handle_product(name, quantity, price, ingredients, origin, notes):
    try:
        existing_product = Product.query.filter_by(ProductName=name).first()
        if existing_product:
            existing_product.Quantity = quantity
            existing_product.Price = price
            db.session.commit()
            product_id = existing_product.ProductID
        else:
            new_product = Product(
                ProductName=name, Quantity=quantity, Price=price,
                Ingredients=ingredients, Origin=origin, Notes=notes
            )
            db.session.add(new_product)
            db.session.commit()
            product_id = new_product.ProductID

        return product_id
    except Exception as e:
        db.session.rollback()
        flash(f'處理產品時發生錯誤: {e}', 'error')
        return None

def handle_images(images, product_id):
    try:
        for idx, image in enumerate(images):
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                # 確保檔名唯一
                filename = f"{product_id}_{idx}_{filename}"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                new_image = ProductImage(ProductID=product_id, ImagePath=filename, ImageOrder=idx)
                db.session.add(new_image)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'處理圖片時發生錯誤: {e}', 'error')


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if not session.get('logged_in'):
        return redirect(url_for('manager_login'))

    if request.method == 'POST':
        data = request.get_json()
        search_target = data.get('target')
        search_value = data.get('value')

        if search_target and search_value:
            all_orders = search_orders(search_target, search_value)
        else:
            all_orders = Orders.query.all()

        return render_template('orders.html', orders=all_orders)

    all_orders = Orders.query.all()
    return render_template('orders.html', orders=all_orders)

def search_orders(target, value):
    if target == 'id' and value.isdigit():
        return Orders.query.filter_by(OrderID=int(value)).all()
    elif target == 'date':
        try:
            search_date = datetime.strptime(value, '%Y-%m-%d')
            end_date = search_date + timedelta(days=1)
            return Orders.query.filter(Orders.OrderDate >= search_date,
                                       Orders.OrderDate < end_date).all()
        except ValueError:
            return []
    elif target == 'phone':
        return db.session.query(OrderDetails).filter(OrderDetails.CustomerPhone.like(f'%{value}%')).all()
    elif target == 'name':
        return Orders.query.filter(Orders.CustomerName.like(f'%{value}%')).all()
    else:
        return []

@app.route('/search_orders', methods=['POST'])
def search_orders_route():
    data = request.get_json()
    target = data.get('target')
    value = data.get('value')

    if target and value:
        if target == 'phone':
            results = db.session.query(OrderDetails).filter(OrderDetails.CustomerPhone.like(f'%{value}%')).all()
        else:
            results = search_orders(target, value)
    else:
        results = []

    def get_status_class(status_type, status_value):
        status_classes = {
            'OrderStatusID': {
                ORDER_STATUS_PENDING: 'status_pending',
                ORDER_STATUS_PROCESSING: 'status_handling',
                ORDER_STATUS_COMPLETED: 'status_complete',
                ORDER_STATUS_CANCELLED: 'status_cancel'
            },
            'PaymentStatusID': {
                PAYMENT_STATUS_UNPAID: 'status_unpaid',
                PAYMENT_STATUS_PAID: 'status_paid',
                PAYMENT_STATUS_CANCELLED: 'status_cancel',
                PAYMENT_STATUS_REFUNDED: 'status_refund'
            },
            'DeliveryStatusID': {
                DELIVERY_STATUS_PREPARING: 'status_handling',
                DELIVERY_STATUS_PROCESSING: 'status_pending',
                DELIVERY_STATUS_SHIPPED: 'status_shipped',
                DELIVERY_STATUS_DELIVERED: 'status_arrived',
                DELIVERY_STATUS_RETURNED: 'status_return',
                DELIVERY_STATUS_CANCELLED: 'status_cancel'
            }
        }
        return status_classes.get(status_type, {}).get(status_value, 'status_unknown')

    if target == 'phone':
        return jsonify([{
            'OrderID': order.OrderID,
            'OrderDate': order.OrderDate.strftime('%Y-%m-%d') if hasattr(order, 'OrderDate') else 'N/A',
            'Status': Orders.get_status_text('OrderStatusID', order.OrderStatusID) if hasattr(order, 'OrderStatusID') else 'N/A',
            'PaymentStatus': Orders.get_status_text('PaymentStatusID', order.PaymentStatusID) if hasattr(order, 'PaymentStatusID') else 'N/A',
            'DeliveryStatus': Orders.get_status_text('DeliveryStatusID', order.DeliveryStatusID) if hasattr(order, 'DeliveryStatusID') else 'N/A',
            'CustomerName': order.CustomerName,
            'TotalPrice': float(order.TotalPrice) if hasattr(order, 'TotalPrice') else 0.0,
            'StatusClass': get_status_class('OrderStatusID', order.OrderStatusID) if hasattr(order, 'OrderStatusID') else 'status_unknown',
            'PaymentStatusClass': get_status_class('PaymentStatusID', order.PaymentStatusID) if hasattr(order, 'PaymentStatusID') else 'status_unknown',
            'DeliveryStatusClass': get_status_class('DeliveryStatusID', order.DeliveryStatusID) if hasattr(order, 'DeliveryStatusID') else 'status_unknown'
        } for order in results])
    else:
        return jsonify([{
            'OrderID': order.OrderID,
            'OrderDate': order.OrderDate.strftime('%Y-%m-%d'),
            'Status': Orders.get_status_text('OrderStatusID', order.OrderStatusID),
            'PaymentStatus': Orders.get_status_text('PaymentStatusID', order.PaymentStatusID),
            'DeliveryStatus': Orders.get_status_text('DeliveryStatusID', order.DeliveryStatusID),
            'CustomerName': order.CustomerName,
            'TotalPrice': float(order.TotalPrice),
            'StatusClass': get_status_class('OrderStatusID', order.OrderStatusID),
            'PaymentStatusClass': get_status_class('PaymentStatusID', order.PaymentStatusID),
            'DeliveryStatusClass': get_status_class('DeliveryStatusID', order.DeliveryStatusID)
        } for order in results])


@app.route('/orders/<int:order_id>', methods=['GET', 'POST'])
def get_orders(order_id):
    order = Orders.query.options(
        db.joinedload(Orders.member),
        db.joinedload(Orders.order_details).joinedload(OrderDetails.product)
    ).filter_by(OrderID=order_id).first_or_404()
    
    if request.method == 'POST':
        data = request.get_json()
        new_order_status = data.get('order_status')
        new_payment_status = data.get('payment_status')
        new_delivery_status = data.get('delivery_status')
        
        if update_order_status(order_id, new_order_status, new_payment_status, new_delivery_status):
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': '更新訂單狀態失敗'}), 400
    
    return render_template('orders.html', order=order)

@app.route('/orderDetail/<int:order_id>')
def orderDetail(order_id):
    # 獲取訂單
    order = db.session.get(Orders, order_id)
    if not order:
        abort(404)  # 如果訂單不存在，返回 404 錯誤

    # 獲取訂單明細
    order_details = db.session.query(OrderDetails).filter(OrderDetails.OrderID == order_id).all()

    # 傳遞訂單和訂單明細到模板
    return render_template('orderDetail.html', order=order, order_details=order_details)


@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    data = request.get_json()
    order_id = data.get('order_id')
    status_type = data.get('status_type')
    new_status = data.get('status')

    if order_id is None or status_type is None or new_status is None:
        return jsonify({'success': False, 'message': '缺少必要參數'}), 400

    if status_type not in ['OrderStatusID', 'PaymentStatusID', 'DeliveryStatusID']:
        return jsonify({'success': False, 'message': '無效的狀態類型'}), 400

    try:
        order = Orders.query.get(order_id)
        if order:
            if status_type == 'OrderStatusID':
                order.OrderStatusID = new_status
            elif status_type == 'PaymentStatusID':
                order.PaymentStatusID = new_status
            elif status_type == 'DeliveryStatusID':
                order.DeliveryStatusID = new_status
            
            db.session.commit()
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': '訂單不存在'}), 404
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新訂單狀態時發生錯誤: {e}")
        return jsonify({'success': False, 'message': '更新失敗'}), 500

@app.route('/api/orders', methods=['GET'])
def api_orders():
    page = int(request.args.get('page', 1))
    status = request.args.get('status', '')
    search = request.args.get('search', '')

    try:
        query = Orders.query

        if status:
            query = query.filter(Orders.OrderStatusID == status)
        
        if search:
            query = query.filter(Orders.CustomerName.like(f'%{search}%'))

        total_orders = query.count()
        orders = query.paginate(page, per_page=10, error_out=False)

        return jsonify({
            'orders': [{
                'order_id': order.OrderID,
                'customer_name': order.CustomerName,
                'total_amount': float(order.TotalPrice),
                'status': order.OrderStatusID
            } for order in orders.items],
            'total_pages': orders.pages,
            'current_page': orders.page
        })
    except Exception as e:
        app.logger.error(f"查詢訂單時發生錯誤: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/products', methods=['GET', 'POST'])
def products():
    if not session.get('logged_in'):
        return redirect(url_for('manager_login'))

    search_target = request.form.get('search_target') if request.method == 'POST' else request.args.get('search_target')
    search_value = request.form.get('search_value', '').strip() if request.method == 'POST' else request.args.get('search_value', '').strip()

    pagination = None
    message = None
    all_products = []

    if search_target:
        if search_target == 'showWeb':
            all_products = Product.query.filter_by(Status=True).order_by(Product.ProductName).all()
        elif search_target == 'availability':
            all_products = Product.query.filter_by(is_available=True).order_by(Product.ProductName).all()
        elif search_target == 'name' and search_value:
            all_products = Product.query.filter(Product.ProductName.ilike(f'%{search_value}%')).order_by(Product.ProductName).all()
        else:
            message = '沒有符合條件的商品'
    else:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        query = Product.query.order_by(
            db.case(
                (Product.is_available == True, 1),
                (Product.Status == True, 2),
                else_=3
            ),
            Product.ProductName
        )
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        all_products = pagination.items

        if not all_products:
            message = '目前沒有商品顯示'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_template('product_list.html', products=all_products)
        return jsonify({'html': html})

    return render_template('products.html', products=all_products, pagination=pagination, message=message)

@app.route('/products/search_by_name', methods=['GET'])
def search_by_name():
    name = request.args.get('name')
    if name:
        products = Product.query.filter(Product.ProductName.like(f'%{name}%')).all()
        return jsonify([product.to_dict() for product in products])
    return jsonify({'status': 'error', 'message': '無效的搜尋關鍵字'}), 400

@app.route('/products/show_web', methods=['GET'])
def show_web():
    products = Product.query.filter_by(Status=True).all()
    return jsonify([product.to_dict() for product in products])

@app.route('/products/availability', methods=['GET'])
def availability():
    products = Product.query.filter_by(is_available=True).all()
    return jsonify([product.to_dict() for product in products])

@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    # 查詢產品
    product = Product.query.get(product_id)
    if not product:
        flash('產品未找到', 'error')
        return redirect(url_for('product_edit', product_id=product_id))
    
    # 獲取來自表單的資料
    product_name = request.form.get('ProductName')
    notes = request.form.get('Notes')
    price = request.form.get('Price')
    quantity = request.form.get('Quantity')
    ingredients = request.form.get('Ingredients')
    origin = request.form.get('Origin')
    
    # 更新產品資料
    updated = False
    if product_name:
        product.ProductName = product_name
        updated = True
    if notes:
        product.Notes = notes
        updated = True
    if price:
        product.Price = price
        updated = True
    if quantity:
        product.Quantity = quantity
        updated = True
    if ingredients:
        product.Ingredients = ingredients
        updated = True
    if origin:
        product.Origin = origin
        updated = True
    
    if updated:
        try:
            # 保存更改到資料庫
            db.session.commit()
            flash('產品資料已更新', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'更新產品資料時發生錯誤: {str(e)}', 'error')
    else:
        flash('沒有任何變更需要更新', 'info')
    
    return redirect(url_for('product_edit', product_id=product_id))

@app.route('/upload_image/<int:product_id>', methods=['POST'])
def upload_image(product_id):
    # 查詢產品
    product = Product.query.get(product_id)
    if not product:
        flash('產品未找到', 'error')
        return redirect(url_for('product_edit', product_id=product_id))
    
    # 檢查是否有選擇圖片
    if 'image' not in request.files:
        flash('沒有選擇圖片', 'error')
        return redirect(url_for('product_edit', product_id=product_id))
    
    image = request.files['image']
    if image.filename == '':
        flash('沒有選擇圖片', 'error')
        return redirect(url_for('product_edit', product_id=product_id))
    
    try:
        filename = secure_filename(image.filename)
        image_path = os.path.join('static/uploads/', filename)
        image.save(image_path)
        
        # 創建新的圖片記錄
        new_image = ProductImage(ProductID=product.ProductID, ImagePath=filename)
        db.session.add(new_image)
        db.session.commit()
        
        flash('圖片上傳成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'上傳圖片時發生錯誤: {str(e)}', 'error')
    
    return redirect(url_for('product_edit', product_id=product_id))

@app.route('/products/toggle_status/<int:product_id>', methods=['POST'])
def toggle_status(product_id):
    product = db.session.get(Product, product_id)
    if product:
        product.Status = not product.Status
        db.session.commit()

        return jsonify({'status': 'success', 'new_status': '上架' if product.Status else '下架'})
    return jsonify({'status': 'error', 'message': '產品不存在'}), 404

@app.route('/products/toggle_availability/<int:product_id>', methods=['POST'])
def toggle_product_availability(product_id):
    product = db.session.get(Product, product_id)
    if product:
        product.is_available = not product.is_available
        db.session.commit()
        return jsonify({'status': 'success', 'is_available': product.is_available})
    return jsonify({'status': 'error', 'message': '產品不存在'}), 404


@app.route('/product/<int:product_id>', methods=['GET'])
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    images = ProductImage.query.filter_by(ProductID=product_id).all()
    return render_template('product_edit.html', product=product, images=images)

@app.route('/delete_image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    # 查找指定的圖片
    image = ProductImage.query.get(image_id)
    
    if image is None:
        flash('圖片未找到', 'error')
        return redirect(url_for('product_edit', product_id=image.ProductID))  # 假設 product_edit 路由需要 product_id 參數
    
    # 刪除圖片
    db.session.delete(image)
    db.session.commit()
    
    flash('圖片已刪除', 'success')
    return redirect(url_for('product_edit', product_id=image.ProductID))

@app.route('/notify_homepage', methods=['POST'])
def notify_homepage():
    try:
        # 實現首頁更新邏輯
        return jsonify({'status': 'success', 'message': '首頁已更新'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/manager_logout')
def manager_logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('manager_login'))

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        # 打印表单验证成功的信息
        print("Form validated successfully")

        # 获取表单数据
        name = form.name.data
        phone = form.phone.data
        email = form.email.data
        password = form.password.data
        birthday = form.birthday.data

        # 打印获取到的数据
        print(f"Name: {name}, Phone: {phone}, Email: {email}, Birthday: {birthday}")

        # 检查是否已存在相同的邮箱或电话
        existing_member = Register.query.filter((Register.Email == email) | (Register.Phone == phone)).first()
        if existing_member:
            flash("此信箱或電話號碼已被註冊", "danger")
        else:
            # 创建新会员并保存到数据库
            member = Register(name=name, phone=phone, email=email, password=password, birthday=birthday)
            db.session.add(member)
            try:
                db.session.commit()
                flash("註冊成功，請登入", "success")
                return redirect(url_for('login'))
            except IntegrityError as e:
                db.session.rollback()
                flash(f"註冊失敗：{str(e)}", "danger")
    else:
        # 如果表单验证未通过，打印错误信息
        print(form.errors)
        flash("表單驗證失敗，請檢查輸入。", "danger")
    
    return render_template('register2.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    next_page = request.args.get('next') or url_for('home')  # Default redirect to home
    if form.validate_on_submit():
        phone = form.phone.data
        password = form.password.data
        member = Register.query.filter_by(Phone=phone).first()
       
        if member and member.check_password(password):
            # Create User instance and log them in
            user = User(id=member.MemberID, name=member.Name, phone=member.Phone, email=member.Email)
            login_user(user)  # Flask-Login handles login state
            
            # Store member_id in session
            session['member_id'] = member.MemberID
           
            # Retrieve cart from session or localStorage
            cart = session.get('cart', [])  # Use session to temporarily store cart
           
            # Save cart items for logged-in user
            if cart:
                for item in cart:
                    product_id = item['product_id']
                    quantity = item['quantity']
                    cart_item = CartItem.query.filter_by(MemberID=user.id, ProductID=product_id).first()
                    if cart_item:
                        cart_item.quantity += quantity
                    else:
                        cart_item = CartItem(MemberID=user.id, ProductID=product_id, Quantity=quantity)
                        db.session.add(cart_item)
                db.session.commit()
                session.pop('cart', None)  # Clear cart from session

            flash("Login successful", "success")
            return redirect(next_page)
        else:
            flash("Invalid login credentials", "danger")
    return render_template('login2.html', form=form)


@app.before_request
def check_login():
    # Remove enforced login logic; check login status only when needed
    pass

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    # Save cart to session
    cart_items = CartItem.query.filter_by(MemberID=current_user.id).all()
    cart = [{'product_id': item.ProductID, 'quantity': item.quantity} for item in cart_items]
    session['cart'] = cart  # Store cart in session
    
    # Clear member_id from session
    session.pop('member_id', None)
    
    logout_user()
    return redirect(url_for('home'))

# LINE 登入路由，目前僅重定向到儀表板
@app.route('/line_login', methods=['GET'])
def line_login():
    # 在此添加 LINE 登入邏輯
    return redirect(url_for('1234.html'))

@app.route('/cart')
@login_required
def cart():
    try:
        # 獲取使用者的購物車項目
        cart_items = CartItem.query.filter_by(MemberID=current_user.id).all()
        return render_template('shoppingcar.html', cart_items=cart_items)
    except Exception as e:
        print(f'Error retrieving cart items: {e}')
        return jsonify({'error': 'An error occurred while retrieving cart items'}), 500

@app.route('/get_product_by_name/<product_name>', methods=['GET'])
def get_product_by_name(product_name):
    product_name = product_name.replace('%20', ' ')  # 處理 URL 編碼中的空格
    product = Product.query.filter_by(ProductName=product_name).first()
    if product:
        return jsonify({
            'ProductID': product.ProductID,
            'name': product.ProductName,
            'price': str(product.Price)
        })
    return jsonify({'error': 'Product not found'}), 404

@app.route('/update_quantity', methods=['POST'])
@login_required
def update_quantity():
    data = request.get_json()
    product_id = data.get('ProductID')
    quantity = data.get('quantity')

    if not product_id or quantity is None:
        return jsonify({'error': '缺少 ProductID 或 quantity'}), 400

    try:
        quantity = int(quantity)
        if quantity < 1:
            return jsonify({'error': '數量必須大於 0'}), 400
    except ValueError:
        return jsonify({'error': '數量必須是數字'}), 400

    cart_item = CartItem.query.filter_by(ProductID=product_id, MemberID=current_user.id).first()
    if not cart_item:
        return jsonify({'error': '找不到該購物車項目'}), 404

    cart_item.quantity = quantity
    db.session.commit()

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': '找不到產品'}), 404

    subtotal = product.Price * quantity

    return jsonify({'subtotal': str(subtotal), 'success': True}), 200

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    try:
        data = request.get_json()
        ProductID = data.get('ProductID')
        quantity = data.get('quantity')

        if ProductID is None or quantity is None:
            return jsonify({'success': False, 'message': 'Invalid data'}), 400

        product = Product.query.get(ProductID)
        if product is None:
            return jsonify({'success': False, 'message': 'Product not found'}), 404

        cart_item = CartItem.query.filter_by(ProductID=ProductID, MemberID=current_user.id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(
                MemberID=current_user.id,
                ProductID=ProductID,
                quantity=quantity
            )
            db.session.add(cart_item)

        db.session.commit()

        subtotal = product.Price * quantity

        return jsonify({'success': True, 'message': 'Item added to cart', 'subtotal': subtotal}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/delete_item', methods=['POST'])
@login_required
def delete_item():
    data = request.json
    ProductID = data.get('ProductID')
   
    cart_item = CartItem.query.filter_by(ProductID=ProductID, MemberID=current_user.id).first()
   
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Item not found'}), 404

@app.route('/member')
@login_required
def member():
    if current_user.is_authenticated:
        member = Register.query.get(current_user.id)
        if member:
            return render_template('member.html', member=member)
   
    return "會員未找到或未登入", 404

@app.route('/member/update', methods=['POST'])
def update_member():
    if not current_user.is_authenticated:
        return jsonify(success=False, message='您需要登入才能更新資料')

    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    member = Register.query.filter_by(MemberID=current_user.id).first()
    if not member:
        return jsonify(success=False, message='用戶不存在')

    # 驗證舊密碼是否正確
    if old_password and not member.check_password(old_password):
        return jsonify(success=False, message='舊密碼錯誤')

    # 驗證新密碼與確認密碼是否一致
    if new_password and new_password != confirm_password:
        return jsonify(success=False, message='新密碼與確認密碼不一致')
    
    # 更新使用者資料
    member.Name = username
    member.Email = email
    member.Phone = phone

    # 如果提供了新密碼，則更新密碼
    if new_password:
        member.set_password(new_password)

    db.session.commit()
    return jsonify(success=True, message='資料更新成功')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 9
    pagination = Product.query.filter_by(Status=True).order_by(
        Product.ProductName,
        Product.is_available.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    # 默認 cart_item_count 為 0，若用戶登入則更新為實際數量
    cart_item_count = 0
    if current_user.is_authenticated:
        member_id = current_user.id
        cart_item_count = CartItem.query.filter_by(MemberID=member_id).count()
   
    # 檢查用戶是否已經登入
    is_authenticated = current_user.is_authenticated

    return render_template('1234.html', products=pagination.items, pagination=pagination, cart_item_count=cart_item_count, is_authenticated=is_authenticated)


@app.route('/api/cart_status')
@login_required
def cart_status():
    try:
        cart_item_count = CartItem.query.filter_by(MemberID=current_user.id).count()
        return jsonify({'cart_item_count': cart_item_count})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = 9
    page_type = request.args.get('page_type', 'group')  # 確定是哪一個頁面在執行搜尋

    if query:
        # 進行搜尋，忽略是否在團購頁面
        products_query = Product.query.filter(Product.ProductName.ilike(f'%{query}%'))
    else:
        products_query = Product.query.filter(Product.Status == True)

    # 處理分頁
    pagination = products_query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    if page_type == 'group':
        # 分別處理可用和不可用產品的分頁
        available_products_query = products_query.filter(Product.is_available == True)
        unavailable_products_query = products_query.filter(Product.is_available == False)

        available_pagination = available_products_query.paginate(page=page, per_page=per_page, error_out=False)
        unavailable_pagination = unavailable_products_query.paginate(page=page, per_page=per_page, error_out=False)

        return render_template('group.html',
                               available_products=available_pagination.items,
                               unavailable_products=unavailable_pagination.items,
                               available_pagination=available_pagination,
                               unavailable_pagination=unavailable_pagination)
    else:
        return render_template('1234.html', products=products, pagination=pagination)

@app.route('/product/<int:product_id>')
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    images = ProductImage.query.filter_by(ProductID=product_id).order_by(ProductImage.ImageOrder).all()
   
    product_data = {
        'ProductName': product.ProductName,
        'Price': str(product.Price),
        'Quantity': product.Quantity,
        'Ingredients': product.Ingredients,
        'Origin': product.Origin,
        'Notes': product.Notes,
        'Images': [image.ImagePath for image in images]
    }
   
    return jsonify(product_data)

@app.route('/product_detail/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    is_authenticated = current_user.is_authenticated  # Ensure this is defined
    return render_template('productDetail.html', product=product, is_authenticated=is_authenticated)

@app.route('/api/product', methods=['GET'])
def fetch_product():
    product_id = request.args.get('ProductID', type=int)
    if product_id:
        product_data = fetch_product_from_database(product_id)
        if product_data:
            return jsonify(product_data)
        else:
            return jsonify({'error': 'Product not found'}), 404
    else:
        return jsonify({'error': 'ProductID is required'}), 400

def fetch_product_from_database(product_id):
    product = Product.query.filter_by(ProductID=product_id).first()
    if product:
        return {
            'ProductID': product.ProductID,
            'ProductName': product.ProductName,
            'Quantity': product.Quantity,
            'Price': product.Price
        }
    return None

@app.route('/group')
def group():
    page = request.args.get('page', 1, type=int)
    per_page = 12  

    # 先對可用產品進行分頁並排序
    available_products_pagination = Product.query.filter_by(is_available=True).order_by(Product.ProductName).paginate(page=page, per_page=per_page, error_out=False)
    available_products = available_products_pagination.items

    # 先對不可用產品進行分頁並排序
    unavailable_products_pagination = Product.query.filter_by(is_available=False).order_by(Product.ProductName).paginate(page=page, per_page=per_page, error_out=False)
    unavailable_products = unavailable_products_pagination.items

    # 默認 cart_item_count 為 0，若用戶登入則更新為實際數量
    cart_item_count = 0
    if current_user.is_authenticated:
        member_id = current_user.id
        cart_item_count = CartItem.query.filter_by(MemberID=member_id).count()

    return render_template(
        'group.html',
        available_products=available_products,
        unavailable_products=unavailable_products,
        available_pagination=available_products_pagination,
        unavailable_pagination=unavailable_products_pagination,
        cart_item_count=cart_item_count  # 傳遞購物車數量到模板
    )

@app.route('/get_products')
def get_products():
    products = Product.query.all()
    products_data = []
    for product in products:
        images = [{'ImagePath': image.ImagePath} for image in product.images]
        products_data.append({
            'ProductID': product.ProductID,
            'ProductName': product.ProductName,
            'Price': product.Price,
            'images': images
        })
    return jsonify({'products': products_data})

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'member_id' not in session:
        return jsonify({'success': False, 'message': '未登入'})

    member_id = session['member_id']
    print(f"Member ID: {member_id}")  

    data = request.get_json()
    cart_items = data.get('cartItems', [])

    if not cart_items:
        return jsonify({'success': False, 'message': '購物車為空'})

    try:
        for item in cart_items:
            product_id = item['productId']
            quantity = item['quantity']

            cart_item = CartItem(MemberID=member_id, ProductID=product_id, quantity=quantity)
            db.session.add(cart_item)

        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/pay', methods=['GET'])
@login_required
def pay():
    if 'member_id' not in session:
        return redirect(url_for('login'))  
    member_id = session['member_id']
    cart_items = db.session.query(CartItem, Product).join(Product, CartItem.ProductID == Product.ProductID)\
                  .filter(CartItem.MemberID == member_id).all()
    cart_items_list = [
        {
            'product': {
                'ProductID': item.Product.ProductID,
                'ProductName': item.Product.ProductName,
                'Price': str(item.Product.Price)
            },
            'CartItem': {
                'id': item.CartItem.id,
                'quantity': item.CartItem.quantity
            }
        }
        for item in cart_items
    ]

    subtotal = sum(float(item['product']['Price']) * item['CartItem']['quantity'] for item in cart_items_list)
    shipping_fee = 50
    total = subtotal + shipping_fee
    return render_template('pay.html', cart_items=cart_items_list, subtotal=subtotal, shipping_fee=shipping_fee, total=total)

@app.route('/order')
@login_required
def order():
    try:
        orders = Orders.query.all()  # 獲取所有訂單資料
        print(f"Orders: {orders}")  # 打印订单数据
        return render_template('order.html', orders=orders)
    except Exception as e:
        print(f"Error retrieving orders: {e}")
        return "An error occurred while retrieving orders.", 500

@app.route('/order_detail/<int:order_id>')
@login_required
def order_detail(order_id):
    try:
        order = db.session.get(Orders, order_id)
        if order is None:
            abort(404)  # 如果找不到訂單，返回 404 錯誤

        # 查詢訂單的詳細資訊
        order_details = db.session.query(OrderDetails).filter_by(OrderID=order_id).all()

        # 確保只取一筆唯一的收貨人資訊
        unique_details = order_details[0] if order_details else None

        return render_template('order-detail.html', order=order, unique_details=unique_details)
    except Exception as e:
        print(f"Error retrieving order detail: {e}")
        return "An error occurred while retrieving the order detail.", 500
 
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = Register.query.filter_by(Email=email).first()
        if user:
            token = secrets.token_urlsafe(16)
            user.reset_token = token
            db.session.commit()
            send_reset_email(user)
            flash('重設密碼的連結已發送到您的電子郵件。', 'info')
            return redirect(url_for('login'))
        else:
            flash('該電子郵件未綁定任何帳號。', 'danger')
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    app.logger.debug(f"重設密碼的 token: {token}")

    user = Register.query.filter_by(reset_token=token).first()
    if not user:
        flash('無效的或已過期的重設連結。', 'danger')
        return redirect(url_for('forgot_password'))

    error_message = None

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or not confirm_password:
            error_message = '請填寫所有必填欄位。'
        elif len(new_password) < 6:
            error_message = '新密碼必須至少6位數。'
        elif new_password != confirm_password:
            error_message = '新密碼與確認密碼不一致。'
        else:
            # 更新使用者密碼
            hashed_password = generate_password_hash(new_password, method='scrypt', salt_length=16)
            user.Password = hashed_password
            user.reset_token = None

            try:
                app.logger.debug(f"嘗試提交資料庫更新: {user.Email}")
                db.session.commit()
                flash('您的密碼已更新。', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'更新密碼時出錯: {str(e)}')
                flash(f'更新密碼時出錯: {str(e)}', 'danger')

    return render_template('reset_password.html', token=token, error_message=error_message)

@app.route('/submit_order', methods=['POST'])
@login_required
def submit_order():
    member_id = current_user.id

    if not member_id:
        return redirect(url_for('login'))

    member = db.session.get(Register, member_id)
    if not member:
        return jsonify({'error': '會員資料未找到'}), 404

    customer_name = member.Name
    customer_phone = member.Phone
    customer_email = member.Email

    data = request.json
    shipping_address = data.get('shippingAddress', '')
    receiver_name = data.get('receiverName', '')
    receiver_phone = data.get('receiverPhone', '')
    remittance_code = data.get('remittanceCode', '')

    if not receiver_name or not receiver_phone:
        return jsonify({'error': '收件人姓名和電話為必填欄位'}), 400

    subtotal = calculate_subtotal(member_id)
    shipping_fee = calculate_shipping_fee()
    total_price = subtotal + shipping_fee

    # 建立訂單
    order = Orders(
        MemberID=member_id,
        CustomerName=customer_name,
        Subtotal=subtotal,
        ShippingFee=shipping_fee,
        TotalPrice=total_price,
        OrderStatusID=ORDER_STATUS_PENDING,
        PaymentStatusID=PAYMENT_STATUS_UNPAID,
        DeliveryStatusID=DELIVERY_STATUS_PREPARING
    )

    db.session.add(order)
    db.session.commit()

    # 新增訂單詳細資訊
    cart_items = data.get('cartItems', [])
    for item in cart_items:
        product = item['product']
       
        # 查詢產品圖片路徑
        product_images = ProductImage.query.filter_by(ProductID=product['ProductID']).all()
        image_path = product_images[0].ImagePath if product_images else None  # 假設取第一張圖片
       
        order_detail = OrderDetails(
            OrderID=order.OrderID,
            ProductID=product['ProductID'],
            ProductName=product['ProductName'],
            ProductImage=image_path,  # 儲存圖片路徑
            UnitPrice=Decimal(product['Price']),
            Quantity=item['CartItem']['quantity'],
            TotalPrice=Decimal(product['Price']) * item['CartItem']['quantity'],
            CustomerName=customer_name,
            CustomerPhone=customer_phone,
            CustomerEmail=customer_email,
            ShippingAddress=shipping_address,
            ReceiverName=receiver_name,
            ReceiverPhone=receiver_phone,
            RemittanceCode=remittance_code
        )

        db.session.add(order_detail)

    db.session.commit()

    # 刪除購物車資料表中的相關項目
    CartItem.query.filter_by(MemberID=member_id).delete()
    db.session.commit()

    return jsonify({'success': True})


    return jsonify({'success': True})

@app.route('/get_product_images', methods=['POST'])
def get_product_images():
    data = request.json
    product_ids = data.get('product_ids', [])
    
    # 查詢產品圖片
    images = ProductImage.query.filter(ProductImage.ProductID.in_(product_ids)).all()
    
    # 格式化圖片路徑
    image_paths = {img.ProductID: img.ImagePath for img in images}
    
    # 返回 JSON 響應
    return jsonify(image_paths)
   
if __name__ == '__main__':
    app.run()
