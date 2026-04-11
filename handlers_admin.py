from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import AdminState
from keyboards import admin_panel_menu, admin_delivery_actions, main_menu, confirm_reset_stats, reset_stats_inline
import database as db
from config import ADMIN_ID

router = Router()

async def is_admin(user_id):
    if str(user_id) == str(ADMIN_ID):
        return True
    admins = await db.get_admins()
    return str(user_id) in admins

@router.message(F.text == "👨‍💻 Admin panel")
async def open_admin_panel(message: Message):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("👨‍💻 Admin panelga xush kelibsiz!", reply_markup=admin_panel_menu())

# --- ADMIN QO'SHISH ---
@router.message(F.text == "➕ Admin qo'shish")
async def ask_admin_id(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("Yangi adminning Telegram ID raqamini kiriting:")
    await state.set_state(AdminState.waiting_for_new_admin_id)

@router.message(AdminState.waiting_for_new_admin_id, F.text)
async def save_new_admin(message: Message, state: FSMContext):
    new_id = message.text.strip()
    if not new_id.isdigit():
        await message.answer("Iltimos, faqat raqamlardan iborat ID kiriting.")
        return
    await db.add_admin(new_id)
    await message.answer(f"✅ Yangi admin muvaffaqiyatli qo'shildi: {new_id}")
    await state.clear()

# --- ADMIN O'CHIRISH ---
@router.message(F.text == "➖ Admin o'chirish")
async def ask_del_admin_id(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("O'chirmoqchi bo'lgan adminning Telegram ID raqamini kiriting:")
    await state.set_state(AdminState.waiting_for_del_admin_id)

@router.message(AdminState.waiting_for_del_admin_id, F.text)
async def delete_admin_handler(message: Message, state: FSMContext):
    del_id = message.text.strip()
    if not del_id.isdigit():
        await message.answer("Iltimos, faqat raqamlardan iborat ID kiriting.")
        return
    if str(del_id) == str(ADMIN_ID):
        await message.answer("Bosh adminni o'chirib bo'lmaydi!")
        return
        
    admins = await db.get_admins()
    if str(del_id) not in admins:
        await message.answer("Bunday admin topilmadi.")
        return
        
    await db.delete_admin(del_id)
    await message.answer(f"✅ Qayd etilgan admin muvaffaqiyatli adminlikdan chiqarildi.")
    await state.clear()

# --- SHIRINLIK QO'SHISH ---
@router.message(F.text == "🍰 Shirinlik qo'shish")
async def ask_product_photo(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("Qo'shilayotgan shirinlik yoki taomning rasmini yuboring:")
    await state.set_state(AdminState.waiting_for_product_photo)

@router.message(AdminState.waiting_for_product_photo, F.photo)
async def process_product_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await message.answer("Ajoyib! Endi shirinlik/taom nomini kiriting:")
    await state.set_state(AdminState.waiting_for_product_name)

@router.message(AdminState.waiting_for_product_name, F.text)
async def process_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"'{message.text}' uchun BUTUNICHA narxini kiriting (raqamlarda, masalan: 120000):")
    await state.set_state(AdminState.waiting_for_product_price_whole)

@router.message(AdminState.waiting_for_product_price_whole, F.text)
async def process_product_price_whole(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqamlarda kiriting:")
        return
    await state.update_data(price_whole=int(message.text))
    await message.answer("Endi ushbu mahsulotning 1 KUSOK uchun narxini kiriting (agar kusokka sotilmasa 0 deb yozing):")
    await state.set_state(AdminState.waiting_for_product_price_slice)

@router.message(AdminState.waiting_for_product_price_slice, F.text)
async def process_product_price_slice(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqamlarda kiriting:")
        return
    data = await state.get_data()
    price_slice = int(message.text)
    
    await db.add_product(
        name=data['name'],
        photo_id=data['photo_id'],
        price_whole=data['price_whole'],
        price_slice=price_slice
    )
    
    await message.answer(
        f"✅ Muvaffaqiyatli qo'shildi!\n\n"
        f"Nomi: {data['name']}\nButunicha: {data['price_whole']} so'm\n"
        f"Kusokka: {price_slice} so'm"
    )
    await state.clear()

# --- SHIRINLIK O'CHIRISH ---
@router.message(F.text == "🗑 Shirinlik o'chirish")
async def show_delete_product_menu(message: Message):
    if not await is_admin(message.from_user.id):
        return
    products = await db.get_products()
    if not products:
        await message.answer("O'chirish uchun shirinliklar mavjud emas.")
        return
    from keyboards import admin_delete_products_keyboard
    await message.answer("Qaysi birini o'chirmoqchisiz? Tanlang:", reply_markup=admin_delete_products_keyboard(products))

@router.callback_query(F.data.startswith("delproduct_"))
async def process_delete_product(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    product_id = int(callback.data.split("_")[1])
    await db.delete_product(product_id)
    await callback.message.edit_text(callback.message.text + "\n\n✅ O'chirildi.")
    await callback.answer("Shirinlik o'chirildi.")

# --- STATISTIKA VA QAYTA TIKLASH ---
@router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message):
    if not await is_admin(message.from_user.id):
        return
        
    today, weekly, monthly = await db.get_statistics()
    
    text = f"""
📊 Statistika "By guli bakery"

Bugun: {today['clients']} ta mijoz, {today['revenue'] or 0} so'm
Shu hafta: {weekly['clients']} ta mijoz, {weekly['revenue'] or 0} so'm
Shu oy: {monthly['clients']} ta mijoz, {monthly['revenue'] or 0} so'm
"""
    await message.answer(text, reply_markup=reset_stats_inline())

@router.callback_query(F.data == "reset_stats_ask")
async def ask_reset_stats(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "Haqiqatdan ham statistikani asliga qaytarmoqchimisiz? (Barcha eski buyurtmalar arxivi o'chib ketadi va hisoblash 0 dan boshlanadi)",
        reply_markup=confirm_reset_stats()
    )

@router.callback_query(F.data == "reset_stats_yes")
async def confirm_reset_stats_yes(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    await db.reset_statistics()
    await callback.message.edit_text("✅ Statistika muvaffaqiyatli asliga qaytarildi! (0 dan boshlanadi)")

@router.callback_query(F.data == "reset_stats_no")
async def confirm_reset_stats_no(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("❌ Bekor qilindi. Statistika joyida qoldi.")

# --- ORDER DELIVERY ACTIONS ---
@router.callback_query(F.data.startswith("admin_sent_"))
async def admin_sent(callback: CallbackQuery, bot: Bot):
    if not await is_admin(callback.from_user.id):
        return
        
    order_id = int(callback.data.split("_")[2])
    await db.update_order_status(order_id, 'sent')
    
    order = await db.get_order(order_id)
    
    try:
        new_text = (callback.message.caption or callback.message.text) + "\n\n👉 Holat: Yuborildi"
        if callback.message.photo:
            await callback.message.edit_caption(caption=new_text, reply_markup=admin_delivery_actions(order_id))
        else:
            await callback.message.edit_text(text=new_text, reply_markup=admin_delivery_actions(order_id))
    except Exception:
        pass
        
    await callback.answer("Buyurtma yuborilganligi belgilandi.")
    
    try:
        if order:
            await bot.send_message(order['user_id'], f"🚚 Buyurtmangiz yo'lga chiqdi! Kuting.")
    except Exception as e:
        print(e)

@router.callback_query(F.data.startswith("admin_delivered_"))
async def admin_delivered(callback: CallbackQuery, bot: Bot):
    if not await is_admin(callback.from_user.id):
        return
        
    order_id = int(callback.data.split("_")[2])
    await db.update_order_status(order_id, 'delivered')
    
    order = await db.get_order(order_id)
    
    try:
        new_text = (callback.message.caption or callback.message.text) + "\n\n✅ Yakunlangan (Mijozga yetib borgan)."
        if callback.message.photo:
            await callback.message.edit_caption(caption=new_text, reply_markup=None)
        else:
            await callback.message.edit_text(text=new_text, reply_markup=None)
    except Exception:
        pass

    await callback.answer("Yakunlandi.")
    
    try:
        if order:
            await bot.send_message(order['user_id'], f"🏁 Buyurtmangiz yetkazib berildi! Yoqimli ishtaha. 'By guli bakery'")
    except Exception as e:
        print(e)
