from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu(is_admin=False):
    kb = [
        [KeyboardButton(text="🛒 Buyurtma berish")]
    ]
    if is_admin:
        kb.append([KeyboardButton(text="👨‍💻 Admin panel")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def cancel_order_inline():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Bekor qilish", callback_data="cancel_order")
    return builder.as_markup()

def phone_keyboard():
    kb = [[KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]]
    kb.append([KeyboardButton(text="🏠 Bosh menyu")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def location_keyboard():
    kb = [[KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True)]]
    kb.append([KeyboardButton(text="🏠 Bosh menyu")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def user_payment_inline(order_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 To'lov qilish", callback_data=f"pay_{order_id}")
    builder.button(text="❌ Bekor qilish", callback_data=f"user_cancel_{order_id}")
    return builder.as_markup()

def admin_order_actions(order_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Buyurtma qabul qilindi", callback_data=f"admin_accept_{order_id}")
    builder.button(text="🚚 Buyurtma yuborildi", callback_data=f"admin_sent_{order_id}")
    builder.button(text="🏁 Mijozda (Yakunlash)", callback_data=f"admin_delivered_{order_id}")
    builder.button(text="❌ Bekor qilish", callback_data=f"admin_cancel_{order_id}")
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()

def admin_panel_menu():
    kb = [
        [KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="🏠 Bosh menyu")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def back_to_main():
    kb = [[KeyboardButton(text="🏠 Bosh menyu")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
