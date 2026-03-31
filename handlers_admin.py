from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import AdminState
from keyboards import admin_panel_menu, admin_order_actions, main_menu
import database as db
from config import ADMIN_ID

router = Router()

def is_admin(user_id):
    return str(user_id) == str(551853004)

@router.message(F.text == "👨‍💻 Admin panel")
async def open_admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
        
    await message.answer("👨‍💻 Admin panelga xush kelibsiz!", reply_markup=admin_panel_menu())

@router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message):
    if not is_admin(message.from_user.id):
        return
        
    today, weekly, monthly = await db.get_statistics()
    
    text = f"""
📊 Statistika "By guli bakery"

Bugun: {today['clients']} ta mijoz, {today['revenue'] or 0} so'm
Shu hafta: {weekly['clients']} ta mijoz, {weekly['revenue'] or 0} so'm
Shu oy: {monthly['clients']} ta mijoz, {monthly['revenue'] or 0} so'm
"""
    await message.answer(text)

@router.callback_query(F.data.startswith("admin_accept_"))
async def admin_accept(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
        
    order_id = int(callback.data.split("_")[2])
    await db.update_order_status(order_id, 'accepted')
    
    await state.set_state(AdminState.waiting_for_price)
    await state.update_data(order_id=order_id, msg_id=callback.message.message_id)
    
    try:
        new_text = callback.message.text + "\n\n👉 Holat: Qabul qilindi, Narx kutilmoqda"
        await callback.message.edit_text(new_text, reply_markup=admin_order_actions(order_id))
    except Exception:
        pass
        
    await callback.message.answer(f"Buyurtma #{order_id} qabul qilindi!\nMijozdan qancha pul olinishini (summani) raqam orqali kiriting:")
    await callback.answer()

@router.message(AdminState.waiting_for_price, F.text)
async def admin_set_price(message: Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqamlar bilan summani kiriting (Masalan, 45000):")
        return
        
    price = int(message.text)
    data = await state.get_data()
    order_id = data['order_id']
    
    await db.update_order_price(order_id, price)
    await message.answer(f"✅ Buyurtma #{order_id} narxi {price} so'm etib belgilandi.")
    
    order = await db.get_order(order_id)
    
    try:
        await bot.send_message(
            order['user_id'], 
            f"✅ Buyurtmangiz qabul qilindi!\nNarxi: {price} so'm.\n"
            f"'To'lov qilish' tugmasi orqali karta raqamini bilishingiz mumkin."
        )
    except Exception as e:
        print(f"Error sending message to user: {e}")
    
    await state.clear()

@router.callback_query(F.data.startswith("admin_sent_"))
async def admin_sent(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return
        
    order_id = int(callback.data.split("_")[2])
    await db.update_order_status(order_id, 'sent')
    
    order = await db.get_order(order_id)
    
    try:
        new_text = callback.message.text + "\n\n👉 Holat: Yuborildi"
        await callback.message.edit_text(new_text, reply_markup=admin_order_actions(order_id))
    except Exception:
        pass
        
    await callback.answer("Buyurtma yuborilganligi belgilandi.")
    
    try:
        await bot.send_message(order['user_id'], f"🚚 Buyurtmangiz yo'lga chiqdi! Kuting.")
    except Exception as e:
        print(e)
        pass

@router.callback_query(F.data.startswith("admin_delivered_"))
async def admin_delivered(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return
        
    order_id = int(callback.data.split("_")[2])
    await db.update_order_status(order_id, 'delivered')
    
    order = await db.get_order(order_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(callback.message.text + "\n\n✅ Yakunlangan (Mijozga yetib borgan).")
    await callback.answer("Yakunlandi.")
    
    try:
        await bot.send_message(order['user_id'], f"🏁 Buyurtmangiz yetkazib berildi! Yoqimli ishtaha. 'By guli bakery'")
    except Exception as e:
        print(e)
        pass

@router.callback_query(F.data.startswith("admin_cancel_"))
async def admin_cancel(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return
        
    order_id = int(callback.data.split("_")[2])
    await db.update_order_status(order_id, 'cancelled')
    
    order = await db.get_order(order_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(callback.message.text + "\n\n❌ Bekor qilingan.")
    await callback.answer("Bekor qilindi.")
    
    try:
        await bot.send_message(order['user_id'], f"❌ Buyurtmangiz admin tomonidan bekor qilindi.")
    except Exception as e:
        print(e)
        pass
