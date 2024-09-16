import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import text, event
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from sqlalchemy.exc import IntegrityError

# 設定圖片上傳的資料夾和允許的檔案類型
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 初始化Flask應用程式和SQLAlchemy
app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:123456@localhost:5432/tealounge'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'supersecretkey'  # 建議使用更複雜和安全的密鑰
db = SQLAlchemy(app)

# 定義Member模型
class Register(db.Model):
    __tablename__ = 'register'
    MemberID = db.Column(db.Integer, primary_key=True, autoincrement=False, server_default=db.text("nextval('member_id_seq')"))
    Name = db.Column(db.String(200), nullable=False)
    Phone = db.Column(db.String(20), nullable=False, unique=True)
    Email = db.Column(db.String(250), nullable=False, unique=True)
    Password = db.Column(db.String(200), nullable=False)
    Birthday = db.Column(db.Date, nullable=False)
    LineID = db.Column(db.String(100))

    def __init__(self, name, phone, email, password, birthday, line_id=None):
        self.Name = name
        self.Phone = phone
        self.Email = email
        self.Password = generate_password_hash(password)
        self.Birthday = birthday
        self.LineID = line_id

    def check_password(self, password):
        return check_password_hash(self.Password, password)

    def __repr__(self):
        return f"<Member {self.Name}>"

def create_sequence(target, connection, **kw):
    connection.execute(text('CREATE SEQUENCE IF NOT EXISTS member_id_seq START 1001'))

event.listen(Register.__table__, 'before_create', create_sequence)

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

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        phone = form.phone.data
        password = form.password.data
        member = Register.query.filter_by(Phone=phone).first()
        if member and member.check_password(password):
            flash("登入成功", "success")
            return redirect(url_for('home', member_id=member.MemberID))  # 修改為重定向到首頁
        else:
            flash("無效的登入憑證", "danger")
    return render_template('mblogin.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        phone = form.phone.data
        email = form.email.data
        password = form.password.data
        birthday = form.birthday.data

        # 檢查是否已經有重複的電子郵件或電話號碼
        existing_member = Register.query.filter((Register.Email == email) | (Register.Phone == phone)).first()
        if existing_member:
            flash("此郵箱或電話號碼已被註冊", "danger")
        else:
            member = Register(name=name, phone=phone, email=email, password=password, birthday=birthday)
            db.session.add(member)
            try:
                db.session.commit()
                flash("註冊成功，請登入", "success")
                return redirect(url_for('login'))
            except IntegrityError as e:
                db.session.rollback()
                flash(f"註冊失敗：{e}", "danger")

    return render_template('register.html', form=form)

# LINE 登入路由，目前僅重定向到儀表板
@app.route('/line_login', methods=['GET'])
def line_login():
    # 在此添加 LINE 登入邏輯
    return redirect(url_for('dashboard'))

# 儀表板路由，顯示會員名稱
@app.route('/dashboard/<int:member_id>')
def dashboard(member_id):
    member = Register.query.get(member_id)
    if member:
        return f"歡迎 {member.Name} 來到 Tealounge！"
    else:
        return "會員未找到", 404

# 創建序列
with app.app_context():
    db.session.execute(text("CREATE SEQUENCE IF NOT EXISTS product_id_seq START 3001"))
    db.session.commit()

class Product(db.Model):
    __tablename__ = 'products'
    ProductID = db.Column(db.Integer, primary_key=True)
    ProductName = db.Column(db.String(100), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    Price = db.Column(db.String(50), nullable=False)

    __table_args__ = (
        db.CheckConstraint('LENGTH("ProductName") >= 2', name='check_productname_len'),
    )

# Define the ProductImage model
class ProductImage(db.Model):
    __tablename__ = 'product_images'
    ImageID = db.Column(db.Integer, primary_key=True)
    ProductID = db.Column(db.Integer, db.ForeignKey('products.ProductID'), nullable=False)
    ImagePath = db.Column(db.String(200), nullable=False)
    ImageOrder = db.Column(db.Integer, nullable=False, default=0)

    product = db.relationship('Product', backref=db.backref('images', lazy=True))

# Ensure sequence starts from 6001
with app.app_context():
    db.session.execute(text("CREATE SEQUENCE IF NOT EXISTS product_image_id_seq START 6001"))
    db.session.commit()

    # Event listener for after_insert
    @event.listens_for(ProductImage, 'after_insert')
    def after_insert_product_image(mapper, connection, target):
        if target.ImageID is None:
            target.ImageID = connection.execute(text("SELECT nextval('product_image_id_seq')")).scalar()

# 檢查文件是否為允許的類型
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure all tables are created
with app.app_context():
    db.create_all()

@app.route('/product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['ProductName']
        quantity = request.form['Quantity']
        price = request.form['Price']
        images = request.files.getlist('images')

        if quantity.strip():  # 檢查是否為空字符串
            try:
                quantity = int(quantity)
            except ValueError:
                flash('數量必須是有效的數字。', 'error')
                return redirect(url_for('add_product'))
        else:
            quantity = None

        # 檢查是否已存在同名商品
        existing_product = Product.query.filter_by(ProductName=name).first()
        if existing_product:
            # 更新現有商品的其他屬性
            existing_product.Quantity = quantity
            existing_product.Price = price
            db.session.commit()
            product_id = existing_product.ProductID
        else:
            # 新增商品
            new_product = Product(ProductName=name, Quantity=quantity, Price=price)
            db.session.add(new_product)
            db.session.commit()
            product_id = new_product.ProductID

        # 處理圖片上傳並設置圖片順序
        for idx, image in enumerate(images):
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)

                # 新增圖片記錄到 ProductImage 表，並設置順序
                new_image = ProductImage(ProductID=product_id, ImagePath=filename, ImageOrder=idx)
                db.session.add(new_image)

        # 如果沒有圖片，預設一個空的圖片順序
        if not images:
            default_image = ProductImage(ProductID=product_id, ImagePath='', ImageOrder=0)
            db.session.add(default_image)

        db.session.commit()
        flash('產品已新增或更新。', 'success')

        return redirect(url_for('add_product'))

    return render_template('product.html')


@app.route('/home')
def home():
    products = Product.query.all()
    for product in products:
        product.images.sort(key=lambda x: x.ImageOrder)  # 根據 ImageOrder 屬性排序圖片列表
    return render_template('1234.html', products=products)

if __name__ == '__main__':
    app.run()
