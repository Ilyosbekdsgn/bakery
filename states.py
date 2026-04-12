from aiogram.fsm.state import State, StatesGroup

class OrderState(StatesGroup):
    waiting_for_product_quantity = State()
    waiting_for_location_or_address = State()
    waiting_for_phone = State()
    waiting_for_receipt = State()
    waiting_for_custom_order_details = State()

class AdminState(StatesGroup):
    waiting_for_product_photo = State()
    waiting_for_product_name = State()
    waiting_for_product_price_whole = State()
    waiting_for_product_price_slice = State()
    waiting_for_new_admin_id = State()
    waiting_for_del_admin_id = State()
    waiting_for_custom_order_price = State()
