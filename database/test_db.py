from flask import Flask, request, abort 
from flask_sqlalchemy import SQLAlchemy 
from linebot import LineBotApi, WebhookHandler 
from linebot.exceptions import InvalidSignatureError 
from linebot.models import MessageEvent, TextMessage, TextSendMessage 
from datetime import datetime
from sqlalchemy import text, Boolean

app = Flask(__name__)

DELIVERY_STATUS_PREPARING = 1  # 備貨中
DELIVERY_STATUS_PROCESSING = 2  # 處理中
DELIVERY_STATUS_SHIPPED = 3  # 已發貨
DELIVERY_STATUS_DELIVERED = 4  # 已送達
DELIVERY_STATUS_RETURNED = 5  # 已退回
DELIVERY_STATUS_CANCELLED = 6  # 已取消


line_bot_api = LineBotApi('b+Bb2VJlaihO1wxMHiA7rd65oSoiPnWGxN5BjbDxDg0tuyWuYhqt40I+BoZwwzhatNEN51JV+nZZMtU2f9CosITrmHQlkFsKAnKG6pO3rCA3SW+HC6uxSxJH+NZiQyj2eTl+asA2/6IhFVAmUg/OcAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('fe4f92453ffda5592e6a2b4151fb7859')

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:123456@localhost:5432/tealounge'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Orders(db.Model):
    __tablename__ = 'orders'  
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=True, server_default=db.text("nextval('order_id_seq')"))
    MemberID = db.Column(db.Integer, db.ForeignKey('register.MemberID'), nullable=False)
    OrderDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    DeliveryStatusID = db.Column(db.Integer, nullable=True, default=DELIVERY_STATUS_PREPARING)


def get_delivered_orders():
    return Orders.query.filter_by(DeliveryStatusID=4).all()


@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/test_db')
def test_db():
    try:
        # 嘗試查詢資料庫
        orders = get_delivered_orders()
        return f"成功連接資料庫，共有 {len(orders)} 筆已到貨的訂單。"
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run() 
