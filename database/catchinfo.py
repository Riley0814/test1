from flask import Flask, request, abort 
from flask_sqlalchemy import SQLAlchemy 
from linebot import LineBotApi, WebhookHandler 
from linebot.exceptions import InvalidSignatureError 
from linebot.models import MessageEvent, TextMessage, TextSendMessage 
from datetime import datetime
from sqlalchemy import text, Boolean

app = Flask(__name__)

# 配送狀態代碼
DELIVERY_STATUS_PREPARING = 1  # 備貨中
DELIVERY_STATUS_PROCESSING = 2  # 處理中
DELIVERY_STATUS_SHIPPED = 3  # 已發貨
DELIVERY_STATUS_DELIVERED = 4  # 已送達
DELIVERY_STATUS_RETURNED = 5  # 已退回
DELIVERY_STATUS_CANCELLED = 6  # 已取消

line_bot_api = LineBotApi('b+Bb2VJlaihO1wxMHiA7rd65oSoiPnWGxN5BjbDxDg0tuyWuYhqt40I+BoZwwzhatNEN51JV+nZZMtU2f9CosITrmHQlkFsKAnKG6pO3rCA3SW+HC6uxSxJH+NZiQyj2eTl+asA2/6IhFVAmUg/OcAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('fe4f92453ffda5592e6a2b4151fb7859')

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:CQ3CvCTEkRzvYyTSQgZoW5gmkkr4yyqP@dpg-cr2po3ij1k6c73ebmgbg-a.singapore-postgres.render.com:5432/tea_lounge'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:123456@localhost:5432/tealounge'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Orders(db.Model):
    __tablename__ = 'orders'  
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=True, server_default=db.text("nextval('order_id_seq')"))
    MemberID = db.Column(db.Integer, db.ForeignKey('register.MemberID'), nullable=False)
    OrderDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    DeliveryStatusID = db.Column(db.Integer, nullable=True, default=DELIVERY_STATUS_PREPARING)

class Product(db.Model):
    __tablename__ = 'products'
    ProductID = db.Column(db.Integer, primary_key=True, server_default=text("nextval('product_id_seq')"))
    ProductName = db.Column(db.String(100), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    Status = db.Column(Boolean, nullable=False, default=False)
    is_available = db.Column(Boolean, nullable=False,default=False)
    __table_args__ = (db.CheckConstraint('LENGTH("ProductName") >= 2', name='check_productname_len'),)  


# 查詢資料庫中狀態為 "delivered" 的訂單
def get_delivered_orders():
    return Orders.query.filter_by(DeliveryStatusID=DELIVERY_STATUS_DELIVERED).all()

@app.route('/test_db')
def test_db():
    try:
        # 嘗試查詢資料庫
        orders = get_delivered_orders()
        return f"成功連接資料庫，共有 {len(orders)} 筆已到貨的訂單。"
    except Exception as e:
        return str(e)


@app.route("/callback", methods=['POST'])  # 定義 Webhook 回調路徑
def callback():
    signature = request.headers['X-Line-Signature']  # 從HTTP標頭中取得X-Line-Signature
    body = request.get_data(as_text=True)  # 取得請求的主體內容
    try:
        handler.handle(body, signature)  # 處理Webhook事件
    except InvalidSignatureError:
        abort(400)  # 如果簽名無效，返回400錯誤
    return 'OK'  # 返回OK表示成功處理

@handler.add(MessageEvent, message=TextMessage)  # 處理 LINE Bot 的訊息事件
def handle_message(event):
    user_message = event.message.text  # 取得使用者發送的訊息
    if user_message.lower() == "check delivered orders":  # 如果訊息是 "我的訂單"
        orders = get_delivered_orders()  # 查詢到貨的訂單
        if orders:
            reply = "已到貨的訂單如下：\n"
            for order in orders:
                reply += f"訂單編號：{order.OrderID}, 商品：{order.ProductName}\n"
        else:
            reply = "目前沒有到貨的訂單。"
    else:
        # 使用 SQLAlchemy 查詢資料庫
        result = Orders.query.filter_by(MemberID=user_message).first()
        if result:
            reply = result.response  # 如果有結果，設定回覆訊息
        else:
            reply = "目前沒有到貨的訂單。"  # 如果沒有結果，設定回覆訊息為"No data found."
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)  # 使用 LINE Bot API 回覆訊息
    )

if __name__ == "__main__":
    app.run() 
