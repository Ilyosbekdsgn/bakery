from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from states import OrderState
from keyboards import main_menu, phone_keyboard, location_keyboard, user_payment_inline, admin_order_actions, back_to_main
import database as db
from config import ADMIN_ID

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    is_admin = str(message.from_user.id) == str(ADMIN_ID)
    await db.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    await message.answer(
        f"Assalomu alaykum! 'By guli bakery' botiga xush kelibsiz.\nQuyidagi menyudan kerakli bo'limni tanlang:",
        reply_markup=main_menu(is_admin)
    )

@router.message(F.text == "🏠 Bosh menyu")
async def process_main_menu(message: Message, state: FSMContext):
    await state.clear()
    is_admin = str(message.from_user.id) == str(ADMIN_ID)
    await message.answer("Bosh menyu", reply_markup=main_menu(is_admin))

# Order Flow
@router.message(F.text == "🛒 Buyurtma berish")
async def start_order(message: Message, state: FSMContext):
    await message.answer("Nima buyurtma qilasiz? (Masalan: Menga 14 ta somsa kerak yoki rasm yuborib tagiga yozishingiz mumkin)", reply_markup=back_to_main())
    await state.set_state(OrderState.waiting_for_order)

@router.message(OrderState.waiting_for_order)
async def process_order_text(message: Message, state: FSMContext):
    if message.text == "🏠 Bosh menyu":
        await process_main_menu(message, state)
        return
        
    photo_id = message.photo[-1].file_id if message.photo else None
    order_text = message.text or message.caption or "Rasm / Sticker / Nomsiz buyurtma"
    await state.update_data(order_text=order_text, photo_id=photo_id)
    await message.answer("Manzilni yozing yoki lokatsiyangizni yuboring:", reply_markup=location_keyboard())
    await state.set_state(OrderState.waiting_for_location_or_address)

@router.message(OrderState.waiting_for_location_or_address)
async def process_order_location(message: Message, state: FSMContext):
    if message.text == "🏠 Bosh menyu":
        await process_main_menu(message, state)
        return
        
    if message.location:
        await state.update_data(
            latitude=message.location.latitude,
            longitude=message.location.longitude,
            address="Lokatsiya orqali yuborildi"
        )
    else:
        await state.update_data(
            latitude=None,
            longitude=None,
            address=message.text
        )
    
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=phone_keyboard())
    await state.set_state(OrderState.waiting_for_phone)

@router.message(OrderState.waiting_for_phone)
async def process_order_phone(message: Message, state: FSMContext, bot: Bot):
    if message.text == "🏠 Bosh menyu":
        await process_main_menu(message, state)
        return
        
    phone = message.contact.phone_number if message.contact else message.text
    data = await state.get_data()
    
    order_id = await db.create_order(
        user_id=message.from_user.id,
        order_text=data['order_text'],
        phone=phone,
        address=data['address'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    
    is_admin = str(message.from_user.id) == str(ADMIN_ID)
    await message.answer(
        "✅ Buyurtmangiz qabul qilindi va adminga yuborildi. Tez orada siz bilan bog'lanamiz!",
        reply_markup=main_menu(is_admin)
    )
    
    await message.answer(
        f"Buyurtma #{order_id}\nHolati: Kutilmoqda\n\nAdmindan narx kutilmoqda. Tasdiqlangandan so'ng to'lov qilishingiz mumkin.",
        reply_markup=user_payment_inline(order_id)
    )
    
    # Notify Admin
    admin_text = (
        f"🆕 *Yangi buyurtma #{order_id}*\n\n"
        f"👤 Mijoz: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"📞 Telefon: {phone}\n"
        f"📍 Manzil: {data['address']}\n"
        f"📝 Buyurtma: {data['order_text']}"
    )
    
    try:
        photo_id = data.get('photo_id')
        has_location = bool(data.get('latitude') and data.get('longitude'))
        
        if photo_id:
            await bot.send_photo(
                chat_id=ADMIN_ID, 
                photo=photo_id, 
                caption=admin_text, 
                parse_mode="Markdown",
                reply_markup=None if has_location else admin_order_actions(order_id)
            )
        else:
            await bot.send_message(
                chat_id=ADMIN_ID, 
                text=admin_text,
                parse_mode="Markdown",
                reply_markup=None if has_location else admin_order_actions(order_id)
            )
            
        if has_location:
            await bot.send_location(
                chat_id=ADMIN_ID, 
                latitude=data['latitude'], 
                longitude=data['longitude'],
                reply_markup=admin_order_actions(order_id)
            )
    except Exception as e:
        print(f"Failed to send to admin: {e}")
        
    await state.clear()

@router.callback_query(F.data.startswith("user_cancel_"))
async def user_cancel_order(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    order = await db.get_order(order_id)
    if not order:
        await callback.answer("Buyurtma topilmadi.", show_alert=True)
        return
        
    if order['status'] in ['sent', 'delivered']:
        await callback.answer("Bu buyurtma allaqachon yuborilgan, bekor qilib bo'lmaydi.", show_alert=True)
        return
        
    await db.update_order_status(order_id, 'cancelled')
    await callback.message.edit_text(callback.message.text + "\n\n❌ Siz bu buyurtmani bekor qildingiz.")
    await callback.answer("Buyurtma bekor qilindi.")
    
    # Notify admin
    try:
        await callback.bot.send_message(ADMIN_ID, f"❌ Mijoz #{order_id} raqamli buyurtmani bekor qildi.")
    except:
        pass

@router.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[1])
    order = await db.get_order(order_id)
    
    if not order:
        await callback.answer("Buyurtma topilmadi.", show_alert=True)
        return
        
    if order['status'] == 'pending':
        await callback.answer("Admin hali buyurtmani qabul qilmadi. Iltimos kuting.", show_alert=True)
        return
        
    text = (
        f"🌟 Buyurtma #{order_id} uchun to'lov ma'lumotlari:\n\n"
        f"Narxi: {order['price']} so'm\n"
        f"Karta raqami: `9860 1606 2979 1890`\n"
        f"Ism Familiya: Toirjonov ilyosbek\n\n"
        f"To'lov qilganingizdan so'ng chekni (rasmni) shu botga yuboring."
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await state.set_state(OrderState.waiting_for_receipt)
    await state.update_data(order_id=order_id)
    await callback.answer()

@router.message(OrderState.waiting_for_receipt, F.photo)
async def process_receipt(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get('order_id')
    if not order_id:
        await state.clear()
        return
        
    await message.answer("✅ To'lov qabul qilindi. Rahmat!")
    
    try:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=f"✅ Buyurtma #{order_id} uchun to'lov (chek) qabul qilindi! Mijoz hisobni amalga oshirdi."
        )
    except Exception as e:
        print(f"Failed to send receipt to admin: {e}")
        
    await state.clear()
