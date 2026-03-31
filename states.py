from aiogram.fsm.state import State, StatesGroup

class OrderState(StatesGroup):
    waiting_for_order = State()
    waiting_for_location_or_address = State()
    waiting_for_phone = State()
    waiting_for_receipt = State()

class AdminState(StatesGroup):
    waiting_for_price = State()
