# services/order_service.py
from models import db, OrderDetails, Orders, Product
from sqlalchemy.sql import text
from flask import current_app as app  # 確保從 Flask 中引入 app

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
