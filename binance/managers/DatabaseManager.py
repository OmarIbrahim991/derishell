import uuid
from binance.models.OrderModel import OrderModel

from binance.util.Util import Util
from binance.util.Database import internal_database

class DatabaseManager:

    def __init__(self):
        pass

    @staticmethod
    def initalize():
        internal_database.connect()
        internal_database.create_tables([OrderModel])

    @staticmethod
    def create_order_entry(orderid, price, contractsize, direction):
        
        orderModel = OrderModel()
        orderModel.orderId = orderid
        orderModel.contractSize = contractsize
        orderModel.price = price
        orderModel.status = "PENDING_CANCEL"
        orderModel.direction = direction
        orderModel.iuid = str(uuid.uuid4())
        orderModel.save()

        return orderModel
 
    @staticmethod
    def create_sl_order_entry(orderid, price, contractsize):
        
        orderModel = OrderModel()
        orderModel.orderId = orderid
        orderModel.contractSize = contractsize
        orderModel.price = price
        orderModel.status = "NEW"
        orderModel.direction = "SELL"
        orderModel.iuid = str(uuid.uuid4())
        orderModel.save()

        return orderModel

    @staticmethod
    def update_new_order_entry(order, orderid, status):
        try:

            orderModel = OrderModel.get(OrderModel.iuid == order.iuid)
            orderModel.orderId = orderid
            orderModel.status = status
            orderModel.save()

            return orderModel

        except:

            Util.get_logger().debug("Failed to retrieve order: " + str(orderid))
            return None  

    @staticmethod
    def update_order_entry(orderid, status):
        
        try:

            orderModel = OrderModel.get(OrderModel.orderId == orderid)
            orderModel.status = status
            orderModel.save()

            return orderModel

        except:

            Util.get_logger().debug("Failed to retrieve order: " + str(orderid))
            return None


    @staticmethod
    def get_order_by_id(orderid):

        try:

            orderModel = OrderModel.get(OrderModel.orderid == orderid)
            return orderModel

        except:

            Util.get_logger().debug("Failed to retrieve order: " + str(orderid))
            return None

    @staticmethod
    def delete_all_order_models():
        models = DatabaseManager.get_all_orders()
        
        for model in models:

            model.delete_instance()

    @staticmethod
    def get_all_orders():
        return OrderModel.select()

    @staticmethod
    def get_all_open_orders():
        return OrderModel.select().where(OrderModel.status == 'NEW')

    @staticmethod
    def get_all_pending_orders():
        return OrderModel.select().where((OrderModel.orderId == '') & (OrderModel.status == "PENDING_CANCEL"))
