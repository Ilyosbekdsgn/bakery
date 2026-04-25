from aiogram.fsm.state import State, StatesGroup

class OrderState(StatesGroup):
    waiting_for_product_quantity = State()
    waiting_for_location_or_address = State()
    waiting_for_phone = State()
    waiting_for_receipt = State()
    waiting_for_custom_order_details = State()
    waiting_for_cake_inscription = State()

class AdminState(StatesGroup):
    waiting_for_product_photo = State()
    waiting_for_product_name = State()
    waiting_for_product_price_whole = State()
    waiting_for_product_price_slice = State()
    waiting_for_new_admin_id = State()
    waiting_for_del_admin_id = State()
    waiting_for_custom_order_price = State()
    
    waiting_for_cake_photo = State()
    waiting_for_cake_name = State()
    waiting_for_cake_price = State()
    waiting_for_cake_description = State()
    
    waiting_for_fast_food_photo = State()
    waiting_for_fast_food_name = State()
    waiting_for_fast_food_price = State()
    waiting_for_fast_food_description = State()
    waiting_for_fast_food_discount_amount = State()

    waiting_for_category_name = State()
    waiting_for_custom_product_photo = State()
    waiting_for_custom_product_name = State()
    waiting_for_custom_product_price = State()
    waiting_for_custom_product_description = State()

    # Thursday discount states
    waiting_for_product_discount_whole = State()
    waiting_for_product_discount_slice = State()
    waiting_for_cake_discount_amount = State()


