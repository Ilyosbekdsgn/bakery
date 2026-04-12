from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from states import OrderState
from keyboards import main_menu, phone_keyboard, location_keyboard, checkout_keyboard, admin_delivery_actions, back_to_main, subscription_keyboard, dynamic_products_keyboard, product_options_inline, admin_custom_order_actions
import database as db
from config import ADMIN_ID
from handlers_admin import is_admin

router = Router()

REQUIRED_CHANNEL = "@BY_GULI_SHIRINLIKLAR_UYI"

async def check_sub(bot: Bot, user_id: int):
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Sub check failed: {e}")
        return False

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await db.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    
    is_subscribed = await check_sub(bot, message.from_user.id)
    if not is_subscribed:
        await message.answer(
            f"Assalomu Alaykum \"By guli bakery\" ga xush kelibsiz!\n\nBotni ishlatish uchun quyidagi kanallarimizga obuna bo'ling:",
            reply_markup=subscription_keyboard()
        )
        return
        
    admin_status = await is_admin(message.from_user.id)
    await message.answer(
        "Bosh menyu:",
        reply_markup=main_menu(admin_status)
    )

@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, bot: Bot):
    is_subscribed = await check_sub(bot, callback.from_user.id)
    if is_subscribed:
        await callback.message.delete()
        admin_status = await is_admin(callback.from_user.id)
        await callback.message.answer(
            "✅ Obuna tasdiqlandi! Bosh menyu:",
            reply_markup=main_menu(admin_status)
        )
    else:
        await callback.answer("Siz hali obuna bo'lmagansiz!", show_alert=True)

@router.message(F.text == "🏠 Bosh menyu")
async def process_main_menu(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    
    is_subscribed = await check_sub(bot, message.from_user.id)
    if not is_subscribed:
        await message.answer(
            "Botni ishlatish uchun quyidagi kanallarimizga obuna bo'ling:",
            reply_markup=subscription_keyboard()
        )
        return
        
    admin_status = await is_admin(message.from_user.id)
    await message.answer("Bosh menyu", reply_markup=main_menu(admin_status))

# --- DYNAMIC MENU ---
@router.message(F.text == "🛒 Buyurtma berish")
async def start_order(message: Message, state: FSMContext, bot: Bot):
    if not await check_sub(bot, message.from_user.id):
        await message.answer("Botni ishlatish uchun obuna bo'ling.", reply_markup=subscription_keyboard())
        return

    products = await db.get_products()
    if not products:
        await message.answer("Hozircha menyuda shirinliklar yo'q.", reply_markup=back_to_main())
        return
        
    await message.answer("Nima buyurtma qilasiz? (Quyidagilardan birini tanlang)", reply_markup=dynamic_products_keyboard(products))

@router.callback_query(F.data == "back_to_products")
async def back_to_products(callback: CallbackQuery):
    products = await db.get_products()
    await callback.message.delete()
    if products:
        await callback.message.answer("Nima buyurtma qilasiz?", reply_markup=dynamic_products_keyboard(products))

@router.callback_query(F.data.startswith("product_"))
async def select_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = await db.get_product(product_id)
    
    caption = f"🍰 *{product['name']}*\n\n🎂 Butunicha narxi: {product['price_whole']} so'm\n"
    if product['price_slice'] > 0:
        caption += f"🍰 Kusok narxi: {product['price_slice']} so'm\n"
        
    caption += "\nQanday xarid qilasiz?"
    
    await callback.message.delete()
    await callback.message.answer_photo(
        photo=product['photo_id'],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=product_options_inline(product_id)
    )

@router.callback_query(F.data == "custom_order")
async def handle_custom_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "Kerakli suratni yuklang yoki nima kerakligi hamda necha pul bo'lishi haqida yozib qoldiring:",
        reply_markup=back_to_main()
    )
    await state.set_state(OrderState.waiting_for_custom_order_details)

@router.message(OrderState.waiting_for_custom_order_details, F.photo | F.text)
async def process_custom_order_details(message: Message, state: FSMContext, bot: Bot):
    if message.text == "🏠 Bosh menyu":
        await process_main_menu(message, state, bot)
        return

    if message.photo:
        photo_id = message.photo[-1].file_id
        order_text = message.caption or "Menyudan tashqari rasmli buyurtma"
        await state.update_data(custom_photo_id=photo_id, order_text=order_text)
    else:
        await state.update_data(order_text=message.text)
        
    await state.update_data(
        is_custom_order=True,
        total_price=0
    )
    
    await message.answer("📍 Manzilni yozing yoki lokatsiyangizni yuboring:", reply_markup=location_keyboard())
    await state.set_state(OrderState.waiting_for_location_or_address)

# --- BUYING WORKFLOW ---
@router.callback_query(F.data.startswith("buy_whole_"))
async def buy_whole(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    product = await db.get_product(product_id)
    
    await state.update_data(
        product_id=product_id,
        order_type="Butun",
        quantity=1,
        total_price=product['price_whole'],
        order_text=f"{product['name']} (Butunicha)"
    )
    
    await callback.message.delete()
    await callback.message.answer("📍 Manzilni yozing yoki lokatsiyangizni yuboring:", reply_markup=location_keyboard())
    await state.set_state(OrderState.waiting_for_location_or_address)

@router.callback_query(F.data.startswith("buy_slice_"))
async def buy_slice(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    product = await db.get_product(product_id)
    
    if product['price_slice'] <= 0:
        await callback.answer("Bu mahsulot kusokka sotilmaydi!", show_alert=True)
        return
        
    await state.update_data(
        product_id=product_id,
        order_type="Kusok",
        price_slice=product['price_slice'],
        product_name=product['name']
    )
    
    await callback.message.delete()
    await callback.message.answer("Qancha kusok olmoqchisiz? Miqdorni raqamlarda kiriting:", reply_markup=back_to_main())
    await state.set_state(OrderState.waiting_for_product_quantity)

@router.message(OrderState.waiting_for_product_quantity, F.text)
async def process_quantity(message: Message, state: FSMContext):
    if message.text == "🏠 Bosh menyu":
        await process_main_menu(message, state, message.bot)
        return
        
    if not message.text.isdigit():
        await message.answer("Iltimos, miqdorni faqat raqamlarda kiriting:")
        return
        
    qty = int(message.text)
    data = await state.get_data()
    total_price = qty * data['price_slice']
    
    await state.update_data(
        quantity=qty,
        total_price=total_price,
        order_text=f"{data['product_name']} ({qty} kusok)"
    )
    
    await message.answer("📍 Manzilni yozing yoki lokatsiyangizni yuboring:", reply_markup=location_keyboard())
    await state.set_state(OrderState.waiting_for_location_or_address)

@router.message(OrderState.waiting_for_location_or_address)
async def process_order_location(message: Message, state: FSMContext):
    if message.text == "🏠 Bosh menyu":
        await process_main_menu(message, state, message.bot)
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
    
    await message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=phone_keyboard())
    await state.set_state(OrderState.waiting_for_phone)

@router.message(OrderState.waiting_for_phone)
async def process_order_phone(message: Message, state: FSMContext, bot: Bot):
    if message.text == "🏠 Bosh menyu":
        await process_main_menu(message, state, bot)
        return
        
    phone = message.contact.phone_number if message.contact else message.text
    data = await state.get_data()
    
    order_id = await db.create_order(
        user_id=message.from_user.id,
        order_text=data['order_text'],
        phone=phone,
        address=data['address'],
        price=data['total_price'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    
    await state.update_data(order_id=order_id)
    admin_status = await is_admin(message.from_user.id)
    
    if data.get('is_custom_order'):
        await message.answer(
            "✅ Buyurtmangiz qabul qilindi va adminga yuborildi!\n"
            "Admin tez orada hisob-kitob qilib, narxni yuboradi. Iltimos botdan keladigan xabarni kuting.",
            reply_markup=main_menu(admin_status)
        )
        
        admin_text = (
            f"🆕 *So'rov: Menyudan tashqari buyurtma #{order_id}*\n\n"
            f"👤 Mijoz: {message.from_user.full_name} (@{message.from_user.username})\n"
            f"📞 Telefon: {phone}\n"
            f"📍 Manzil: {data['address']}\n"
            f"📝 Tafsilotlar: {data.get('order_text', 'Bo`sh')}\n"
        )
        admins = await db.get_admins()
        for ad_id in admins:
            try:
                if data.get('custom_photo_id'):
                    await bot.send_photo(chat_id=ad_id, photo=data['custom_photo_id'], caption=admin_text, reply_markup=admin_custom_order_actions(order_id), parse_mode="Markdown")
                else:
                    await bot.send_message(chat_id=ad_id, text=admin_text, reply_markup=admin_custom_order_actions(order_id), parse_mode="Markdown")
                
                if data.get('latitude') and data.get('longitude'):
                    await bot.send_location(chat_id=ad_id, latitude=data['latitude'], longitude=data['longitude'])
            except Exception:
                pass
        await state.clear()
        return

    await message.answer(
        "✅ Buyurtmalaringiz muvaffaqiyatli yig'ildi!",
        reply_markup=main_menu(admin_status)
    )
    
    await message.answer(
        f"Buyurtma #{order_id}\n📝 {data['order_text']}\n💳 Jami summa: {data['total_price']} so'm\n\n"
        "Pastdagi to'lov qilish tugmasi orqali marshrut chekini botga yuboring:",
        reply_markup=checkout_keyboard(order_id)
    )
    await state.set_state(OrderState.waiting_for_receipt)

@router.callback_query(F.data.startswith("user_cancel_"))
async def user_cancel_order(callback: CallbackQuery, state: FSMContext):
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
    await state.clear()
    
    try:
        admins = await db.get_admins()
        for ad_id in admins:
            await callback.bot.send_message(ad_id, f"❌ Mijoz #{order_id} raqamli buyurtmani bekor qildi.")
    except:
        pass

@router.callback_query(F.data.startswith("pay_cash_"))
async def process_pay_cash(callback: CallbackQuery, state: FSMContext, bot: Bot):
    order_id = int(callback.data.split("_")[2])
    order = await db.get_order(order_id)
    if not order:
        return await callback.answer("Buyurtma topilmadi.", show_alert=True)
        
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("✅ Buyurtmangiz qabul qilindi, tez orada yetkazib beramiz! (To'lov olinganda qilinadi)")
    
    data = await state.get_data()
    product_id = data.get('product_id')
    product = None
    if product_id:
        product = await db.get_product(product_id)
        
    admin_text = (
        f"🆕 *Yangi Buyurtma #{order_id}*\n\n"
        f"👤 Mijoz: {callback.from_user.full_name} (@{callback.from_user.username})\n"
        f"📞 Telefon: {order['phone']}\n"
        f"📍 Manzil: {order['address']}\n"
        f"📝 Buyurtma: {order['order_text']}\n"
        f"💰 Summa: {order['price']} so'm\n"
        f"💵 *To'lov usuli: Olinganda to'lash deb belgilandi*\n"
    )
    
    admins = await db.get_admins()
    for ad_id in admins:
        try:
            if product and product['photo_id']:
                await bot.send_photo(chat_id=ad_id, photo=product['photo_id'], caption=admin_text, parse_mode="Markdown")
            else:
                await bot.send_message(chat_id=ad_id, text=admin_text, parse_mode="Markdown")
                
            if order['latitude'] and order['longitude']:
                await bot.send_location(chat_id=ad_id, latitude=order['latitude'], longitude=order['longitude'])
                
            from keyboards import admin_delivery_actions
            await bot.send_message(chat_id=ad_id, text=f"Buyurtma #{order_id} boshqaruvi:", reply_markup=admin_delivery_actions(order_id))
        except Exception as e:
            print(f"Error {e}")
            
    await state.clear()
    await callback.answer()

@router.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[1])
    order = await db.get_order(order_id)
    
    if not order:
        await callback.answer("Buyurtma topilmadi.", show_alert=True)
        return
        
    await state.update_data(order_id=order_id)
    await state.set_state(OrderState.waiting_for_receipt)
        
    text = (
        f"🌟 Buyurtma #{order_id} to'lov ma'lumotlari:\n\n"
        f"Narxi: {order['price']} so'm\n"
        f"Karta raqami: `4067 0700 0058 0113`\n"
        f"Ism Familiya: Ortiqov Izzatillo\n\n"
        f"💳 To'lov qilganingizdan so'ng chekni (rasmni) shu botga yuboring."
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@router.message(OrderState.waiting_for_receipt, F.photo)
async def process_receipt(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get('order_id')
    product_id = data.get('product_id')
    
    if not order_id:
        return
        
    order = await db.get_order(order_id)
    if not order:
        return

    product = None
    if product_id:
        product = await db.get_product(product_id)

    await message.answer("✅ Buyurtmangiz qabul qilindi, tez orada yetkazib beramiz!")
    
    receipt_photo = message.photo[-1].file_id
    admin_text = (
        f"🆕 *Yangi Buyurtma #{order_id}*\n\n"
        f"👤 Mijoz: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"📞 Telefon: {order['phone']}\n"
        f"📍 Manzil: {order['address']}\n"
        f"📝 Buyurtma: {order['order_text']}\n"
        f"💰 Tolov qilingan summa: {order['price']} so'm\n"
    )
    
    admins = await db.get_admins()
    for ad_id in admins:
        try:
            # 1. Product photo and details
            if product and product['photo_id']:
                await bot.send_photo(
                    chat_id=ad_id,
                    photo=product['photo_id'],
                    caption=admin_text,
                    parse_mode="Markdown"
                )
            else:
                await bot.send_message(
                    chat_id=ad_id,
                    text=admin_text,
                    parse_mode="Markdown"
                )
                
            # 2. Location (if present)
            if order['latitude'] and order['longitude']:
                await bot.send_location(
                    chat_id=ad_id, 
                    latitude=order['latitude'], 
                    longitude=order['longitude']
                )

            # 3. Receipt with action buttons (always last)
            await bot.send_photo(
                chat_id=ad_id,
                photo=receipt_photo,
                caption="💳 To'lov cheki:",
                reply_markup=admin_delivery_actions(order_id)
            )
        except Exception as e:
            print(f"Failed to send to admin {ad_id}: {e}")
            
    await state.clear()
