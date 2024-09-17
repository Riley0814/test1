from flask import Flask, request, abort  # 引入 Flask 框架和相關模組
from flask_sqlalchemy import SQLAlchemy  # 引入 SQLAlchemy 模組
from linebot import LineBotApi, WebhookHandler  # 引入 LINE Bot API 和 Webhook 處理器
from linebot.exceptions import InvalidSignatureError  # 引入 LINE Bot API 的例外處理
from linebot.models import MessageEvent, TextMessage, TextSendMessage  # 引入 LINE Bot API 的訊息模型

line_bot_api = LineBotApi('b+Bb2VJlaihO1wxMHiA7rd65oSoiPnWGxN5BjbDxDg0tuyWuYhqt40I+BoZwwzhatNEN51JV+nZZMtU2f9CosITrmHQlkFsKAnKG6pO3rCA3SW+HC6uxSxJH+NZiQyj2eTl+asA2/6IhFVAmUg/OcAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('fe4f92453ffda5592e6a2b4151fb7859')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:123456@localhost:5432/tealounge'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定義資料庫中的 Order 模型
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)  # 訂單編號
    user_id = db.Column(db.String)  # 使用者 ID
    product_name = db.Column(db.String)  # 商品名稱
    quantity = db.Column(db.Integer)  # 商品數量
    status = db.Column(db.String)  # 訂單狀態

# 查詢資料庫中狀態為 "delivered" 的訂單
def get_delivered_orders():
    return Order.query.filter_by(status='delivered').all()

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
    if user_message.lower() == "我的訂單":  # 如果訊息是 "我的訂單"
        orders = get_delivered_orders()  # 查詢到貨的訂單
        if orders:
            reply = "已到貨的訂單如下：\n"
            for order in orders:
                reply += f"訂單編號：{order.id}, 商品：{order.product_name}, 數量：{order.quantity}\n"
        else:
            reply = "目前沒有到貨的訂單。"
    else:
        # 使用 SQLAlchemy 查詢資料庫
        result = Order.query.filter_by(query=user_message).first()
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
