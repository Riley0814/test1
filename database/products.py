import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import text

# 設定圖片上傳的資料夾和允許的檔案類型
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 初始化Flask應用程式和SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:123456@localhost:5432/tealounge'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'
db = SQLAlchemy(app)

# 創建序列
with app.app_context():
    db.session.execute(text("CREATE SEQUENCE IF NOT EXISTS product_id_seq START 3001"))
    db.session.commit()

# 定義Product模型
class Product(db.Model):
    __tablename__ = 'products'
    ProductID = db.Column(db.Integer, primary_key=True, server_default=text("nextval('product_id_seq')"))
    ProductName = db.Column(db.String(100), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    Price = db.Column(db.String(50), nullable=False)

    __table_args__ = (
        db.CheckConstraint('LENGTH("ProductName") >= 2', name='check_productname_len'),
    )

# 定義ProductImage模型
class ProductImage(db.Model):
    __tablename__ = 'product_images'
    ImageID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProductID = db.Column(db.Integer, db.ForeignKey('products.ProductID'), nullable=False)
    ImagePath = db.Column(db.String(200), nullable=False)

    product = db.relationship('Product', backref=db.backref('images', lazy=True))

# 檢查文件是否為允許的類型
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['ProductName']
        quantity = request.form['Quantity']
        price = request.form['Price']
        images = request.files.getlist('images')

        # 檢查數量是否為空字符串或不是有效數字
        if quantity.strip():  # 檢查是否為空字符串
            try:
                quantity = int(quantity)
            except ValueError:
                flash('數量必須是有效的數字。', 'error')
                return redirect(url_for('add_product'))
        else:
            quantity = None

        # 新增產品
        new_product = Product(ProductName=name, Quantity=quantity, Price=price)
        try:
            db.session.add(new_product)
            db.session.commit()

            # 處理圖片上傳
            for image in images:
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)

                    # 新增圖片記錄到ProductImage表
                    new_image = ProductImage(ProductID=new_product.ProductID, ImagePath=image_path)
                    db.session.add(new_image)

            db.session.commit()
            flash('產品已新增。', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'新增產品時發生錯誤：{str(e)}', 'error')

        return redirect(url_for('add_product'))

    return render_template('product.html')

# 在應用程式上下文中創建所有資料庫表
with app.app_context():
    db.create_all()

# 顯示首頁和產品列表
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('1234.html', products=products)

# 啟動應用程式
if __name__ == '__main__':
    # 確保上傳資料夾存在
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run()
