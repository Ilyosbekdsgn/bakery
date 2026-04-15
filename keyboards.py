from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def subscription_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Kanalga obuna bo'lish", url="https://t.me/BY_GULI_SHIRINLIKLAR_UYI")
    builder.button(text="📸 Instagramga obuna bo'lish", url="https://www.instagram.com/by_guli_bakery?igsh=MTh1OTNxajI1NXBiNA==")
    builder.button(text="✅ Tasdiqlash", callback_data="check_subscription")
    builder.adjust(1)
    return builder.as_markup()

def main_menu(is_admin=False):
    kb = [
        [KeyboardButton(text="🛒 Buyurtma berish")],
        [KeyboardButton(text="🛒 Savatim")]
    ]
    if is_admin:
        kb.append([KeyboardButton(text="👨‍💻 Admin panel")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def admin_panel_menu():
    kb = [
        [KeyboardButton(text="🍰 Shirinlik qo'shish"), KeyboardButton(text="🗑 Shirinlik o'chirish")],
        [KeyboardButton(text="➕ Admin qo'shish"), KeyboardButton(text="➖ Admin o'chirish")],
        [KeyboardButton(text="🎉 Payshanba skidkasi")],
        [KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="🏠 Bosh menyu")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def thursday_discount_menu():
    kb = [
        [KeyboardButton(text="🍰 Shirinliklarga skidka qilish"), KeyboardButton(text="🎂 Tortlarga skidka qilish")],
        [KeyboardButton(text="🔥 Skidkani yoqish"), KeyboardButton(text="⛔️ Skidkani to'xtatish")],
        [KeyboardButton(text="🏠 Bosh menyu")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def reset_stats_inline():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Statistikani asliga qaytarish", callback_data="reset_stats_ask")
    return builder.as_markup()

def confirm_reset_stats():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha", callback_data="reset_stats_yes")
    builder.button(text="❌ Yo'q", callback_data="reset_stats_no")
    builder.adjust(2)
    return builder.as_markup()

def dynamic_products_keyboard(products, is_discount=False):
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(text=product['name'], callback_data=f"product_{product['id']}")
    builder.button(text="🎂 Tortlar", callback_data="cakes_menu")
    builder.button(text="📝 Menyudan tashqari buyurtma", callback_data="custom_order")
    builder.adjust(1)
    return builder.as_markup()

def dynamic_cakes_keyboard(cakes, is_discount=False):
    builder = InlineKeyboardBuilder()
    for cake in cakes:
        price = cake['price']
        if is_discount:
            price = max(0, price - cake['discount_amount'])
        builder.button(text=f"{cake['name']} {price}", callback_data=f"cake_{cake['id']}")
    builder.button(text="↩️ Orqaga", callback_data="back_to_products")
    builder.adjust(1)
    return builder.as_markup()

def admin_discount_products_keyboard(products):
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(text=f"🎁 {product['name']}", callback_data=f"discproduct_{product['id']}")
    builder.adjust(1)
    return builder.as_markup()

def admin_discount_cakes_keyboard(cakes):
    builder = InlineKeyboardBuilder()
    for cake in cakes:
        builder.button(text=f"🎁 {cake['name']}", callback_data=f"disccake_{cake['id']}")
    builder.adjust(1)
    return builder.as_markup()

def admin_delete_products_keyboard(products):
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(text=f"❌ {product['name']}", callback_data=f"delproduct_{product['id']}")
    builder.adjust(1)
    return builder.as_markup()

def admin_delete_cakes_keyboard(cakes):
    builder = InlineKeyboardBuilder()
    for cake in cakes:
        builder.button(text=f"❌ {cake['name']}", callback_data=f"delcake_{cake['id']}")
    builder.adjust(1)
    return builder.as_markup()

def product_options_inline(product_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="🎂 Butunicha", callback_data=f"buy_whole_{product_id}")
    builder.button(text="🍰 Kusokka", callback_data=f"buy_slice_{product_id}")
    builder.button(text="↩️ Orqaga", callback_data="back_to_products")
    builder.adjust(2, 1)
    return builder.as_markup()

def cake_options_inline(cake_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Buyurtma berish", callback_data=f"buy_cake_{cake_id}")
    builder.button(text="✍️ Ustiga yozuv yozdirish", callback_data=f"write_cake_{cake_id}")
    builder.button(text="↩️ Orqaga", callback_data="cakes_menu")
    builder.adjust(1)
    return builder.as_markup()

def admin_add_category_inline():
    builder = InlineKeyboardBuilder()
    builder.button(text="🍰 Shirinlik", callback_data="add_shirinlik")
    builder.button(text="🎂 Tort", callback_data="add_cake_admin")
    builder.adjust(2)
    return builder.as_markup()

def admin_delete_category_inline():
    builder = InlineKeyboardBuilder()
    builder.button(text="🍰 Shirinlik", callback_data="del_shirinlik")
    builder.button(text="🎂 Tort", callback_data="del_cake_admin")
    builder.adjust(2)
    return builder.as_markup()

def phone_keyboard():
    kb = [[KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]]
    kb.append([KeyboardButton(text="🏠 Bosh menyu")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def location_keyboard():
    kb = [[KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True)]]
    kb.append([KeyboardButton(text="🏠 Bosh menyu")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def checkout_keyboard(order_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 To'lov qilish", callback_data=f"pay_{order_id}")
    builder.button(text="💵 Olinganda to'lash", callback_data=f"pay_cash_{order_id}")
    builder.button(text="❌ Bekor qilish", callback_data=f"user_cancel_{order_id}")
    builder.adjust(1)
    return builder.as_markup()

def admin_delivery_actions(order_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="🚚 Buyurtma yuborildi", callback_data=f"admin_sent_{order_id}")
    builder.button(text="🏁 Mijozga yetkazib berildi", callback_data=f"admin_delivered_{order_id}")
    builder.adjust(1)
    return builder.as_markup()

def admin_custom_order_actions(order_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="💰 Summa kiritish", callback_data=f"admin_set_price_{order_id}")
    builder.adjust(1)
    return builder.as_markup()

def back_to_main():
    kb = [[KeyboardButton(text="🏠 Bosh menyu")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def continue_or_cart_inline():
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Savatga o'tish", callback_data="view_cart")
    builder.button(text="🍕 Davom etish", callback_data="back_to_products")
    builder.adjust(1)
    return builder.as_markup()

def cart_actions_inline():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Buyurtmani rasmiylashtirish", callback_data="checkout_cart")
    builder.button(text="🗑 Savatni tozalash", callback_data="clear_cart")
    builder.adjust(1)
    return builder.as_markup()
