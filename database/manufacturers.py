from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:123456@localhost:5432/tealounge'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定義 Manufacturer 表
class Manufacturer(db.Model):
    __tablename__ = 'manufacturers'
    ManufacturerID = db.Column(db.Integer, primary_key=True, autoincrement=False, server_default=db.text("nextval('manufacturer_id_seq')"))
    ProductID = db.Column(db.Integer, nullable=False)
    ManufacturerName = db.Column(db.String(100), nullable=False)
    ManufacturerPhone = db.Column(db.String(15), nullable=False)
    ManufacturerAddress = db.Column(db.String(200), nullable=False)

# 創建序列
def create_sequence(target, connection, **kw):
    connection.execute(text('CREATE SEQUENCE IF NOT EXISTS manufacturer_id_seq START 2001'))

# 在 Manufacturer 表創建之前創建序列
event.listen(Manufacturer.__table__, 'before_create', create_sequence)

# 創建數據庫和表
with app.app_context():
    db.create_all()

# 插入數據
with app.app_context():
    manufacturers = [
        Manufacturer(ProductID=3006, ManufacturerName='本家生機食材有限公司', ManufacturerPhone='032180480', ManufacturerAddress='330桃園市桃園區建國東路15巷5號'),
        Manufacturer(ProductID=3007, ManufacturerName='本家生機食材有限公司', ManufacturerPhone='032180480', ManufacturerAddress='330桃園市桃園區建國東路15巷5號'),
        Manufacturer(ProductID=3001, ManufacturerName='喬山健康科技股份有限公司東大分公司', ManufacturerPhone='0800866688', ManufacturerAddress='台中市大雅區東大路2段999號'),
        Manufacturer(ProductID=3002, ManufacturerName='喬山健康科技股份有限公司東大分公司', ManufacturerPhone='0800866688', ManufacturerAddress='台中市大雅區東大路2段999號'),
        Manufacturer(ProductID=3003, ManufacturerName='喬山健康科技股份有限公司東大分公司', ManufacturerPhone='0800866688', ManufacturerAddress='台中市大雅區東大路2段999號'),
        Manufacturer(ProductID=3004, ManufacturerName='喬山健康科技股份有限公司東大分公司', ManufacturerPhone='0800866688', ManufacturerAddress='台中市大雅區東大路2段999號'),
        Manufacturer(ProductID=3005, ManufacturerName='喬山健康科技股份有限公司東大分公司', ManufacturerPhone='0800866688', ManufacturerAddress='台中市大雅區東大路2段999號'),
        Manufacturer(ProductID=3009, ManufacturerName='華南盒餐', ManufacturerPhone='0227732170', ManufacturerAddress='台北市內湖區環山路二段53巷5弄2號'),
        Manufacturer(ProductID=3010, ManufacturerName='華南盒餐', ManufacturerPhone='0227732170', ManufacturerAddress='台北市內湖區環山路二段53巷5弄2號'),
        Manufacturer(ProductID=3015, ManufacturerName='昌祐國際有限公司', ManufacturerPhone='0225580986', ManufacturerAddress='台北市南京西路344巷41號1F'),
        Manufacturer(ProductID=3016, ManufacturerName='昌祐國際有限公司', ManufacturerPhone='0225580986', ManufacturerAddress='台北市南京西路344巷41號1F'),
        Manufacturer(ProductID=3017, ManufacturerName='昌祐國際有限公司', ManufacturerPhone='0225580986', ManufacturerAddress='台北市南京西路344巷41號1F'),
        Manufacturer(ProductID=3018, ManufacturerName='昌祐國際有限公司', ManufacturerPhone='0225580986', ManufacturerAddress='台北市南京西路344巷41號1F'),
        Manufacturer(ProductID=3019, ManufacturerName='昌祐國際有限公司', ManufacturerPhone='0225580986', ManufacturerAddress='台北市南京西路344巷41號1F')
    ]
    db.session.bulk_save_objects(manufacturers)
    db.session.commit()

if __name__ == '__main__':
    app.run()
