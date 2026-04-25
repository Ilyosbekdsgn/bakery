from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import AdminState
from keyboards import admin_panel_menu, admin_delivery_actions, main_menu, confirm_reset_stats, reset_stats_inline, admin_add_category_inline, admin_delete_category_inline, thursday_discount_menu, admin_discount_products_keyboard, admin_discount_cakes_keyboard
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

# --- SHIRINLIK YOKI TORT QO'SHISH ---
@router.message(F.text == "📦 Mahsulot qo'shish")
async def ask_add_category(message: Message):
    if not await is_admin(message.from_user.id):
        return
    categories = await db.get_categories()
    await message.answer("Nimani qo'shmoqchisiz?", reply_markup=admin_add_category_inline(categories))

@router.callback_query(F.data == "add_shirinlik")
async def ask_product_photo(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("Qo'shilayotgan shirinlik yoki taomning rasmini yuboring:")
    await state.set_state(AdminState.waiting_for_product_photo)
    await callback.answer()

@router.callback_query(F.data == "add_cake_admin")
async def ask_cake_photo(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("Qo'shilayotgan tortning rasmini yuklang:")
    await state.set_state(AdminState.waiting_for_cake_photo)
    await callback.answer()

@router.message(AdminState.waiting_for_cake_photo, F.photo)
async def process_cake_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await message.answer("Tortning nomini kiriting:")
    await state.set_state(AdminState.waiting_for_cake_name)

@router.message(AdminState.waiting_for_cake_name, F.text)
async def process_cake_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Tortning narxini kiriting (raqamlarda, masalan 100000):")
    await state.set_state(AdminState.waiting_for_cake_price)

@router.message(AdminState.waiting_for_cake_price, F.text)
async def process_cake_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Iltimos, faqat raqamlarda kiriting:")
    await state.update_data(price=int(message.text))
    await message.answer("Tort haqida malumotlarni yozib qoldiring:")
    await state.set_state(AdminState.waiting_for_cake_description)

@router.message(AdminState.waiting_for_cake_description, F.text)
async def process_cake_description(message: Message, state: FSMContext):
    data = await state.get_data()
    description = message.text
    
    await db.add_cake(
        name=data['name'],
        photo_id=data['photo_id'],
        price=data['price'],
        description=description
    )
    
    await message.answer(f"✅ Muvaffaqiyatli qo'shildi!\n\nNomi: {data['name']}\nNarxi: {data['price']} so'm\nM'alumot: {description}")
    await state.clear()

@router.callback_query(F.data == "add_fastfood_admin")
async def ask_fastfood_photo(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("Qo'shilayotgan fast foodning rasmini yuklang:")
    await state.set_state(AdminState.waiting_for_fast_food_photo)
    await callback.answer()

@router.message(AdminState.waiting_for_fast_food_photo, F.photo)
async def process_fastfood_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await message.answer("Fast food nomini kiriting:")
    await state.set_state(AdminState.waiting_for_fast_food_name)

@router.message(AdminState.waiting_for_fast_food_name, F.text)
async def process_fastfood_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Fast food narxini kiriting (raqamlarda, masalan 15000):")
    await state.set_state(AdminState.waiting_for_fast_food_price)

@router.message(AdminState.waiting_for_fast_food_price, F.text)
async def process_fastfood_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Iltimos, faqat raqamlarda kiriting:")
    await state.update_data(price=int(message.text))
    await message.answer("Fast food haqida malumot yozib yuboring:")
    await state.set_state(AdminState.waiting_for_fast_food_description)

@router.message(AdminState.waiting_for_fast_food_description, F.text)
async def process_fastfood_description(message: Message, state: FSMContext):
    data = await state.get_data()
    description = message.text
    
    await db.add_fast_food(
        name=data['name'],
        photo_id=data['photo_id'],
        price=data['price'],
        description=description
    )
    
    await message.answer(f"✅ Muvaffaqiyatli qo'shildi!\n\nNomi: {data['name']}\nNarxi: {data['price']} so'm\nM'alumot: {description}")
    await state.clear()

# --- MENYU QO'SHISH VA O'CHIRISH ---
@router.message(F.text == "📂 Menyu qo'shish")
async def ask_add_custom_menu(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await message.answer("Yangi menyu nomini kiriting (Masalan: Ichimliklar 🍹):")
    await state.set_state(AdminState.waiting_for_category_name)

@router.message(AdminState.waiting_for_category_name, F.text)
async def process_add_custom_menu(message: Message, state: FSMContext):
    name = message.text
    try:
        await db.add_category(name)
        await message.answer(f"✅ '{name}' menyusi muvaffaqiyatli qo'shildi!")
    except Exception as e:
        await message.answer("Xatolik! Balki bunday menyu allaqachon bordir.")
    await state.clear()

@router.message(F.text == "🗑 Menyu o'chirish")
async def ask_del_custom_menu(message: Message):
    if not await is_admin(message.from_user.id): return
    categories = await db.get_categories()
    if not categories:
        return await message.answer("O'chirish uchun dinamik menyular mavjud emas.")
    from keyboards import admin_delete_menu_inline
    await message.answer("Qaysi menyuni o'chirmoqchisiz? Barcha vidjetlari qo'shilib o'chib ketadi!", reply_markup=admin_delete_menu_inline(categories))

@router.callback_query(F.data.startswith("rm_cat_"))
async def process_del_custom_menu(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id): return
    cat_id = int(callback.data.split("_")[2])
    cat = await db.get_category(cat_id)
    if cat:
        await db.delete_category(cat_id)
        await callback.message.edit_text(f"✅ '{cat['name']}' menyusi barcha mahsulotlari bilan o'chirildi.")
    await callback.answer()

@router.callback_query(F.data.startswith("add_custom_prod_"))
async def ask_custom_product_photo(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id): return
    cat_id = int(callback.data.split("_")[3])
    await state.update_data(target_category_id=cat_id)
    await callback.message.edit_text("Qo'shilayotgan mahsulotning rasmini yuklang:")
    await state.set_state(AdminState.waiting_for_custom_product_photo)
    await callback.answer()

@router.message(AdminState.waiting_for_custom_product_photo, F.photo)
async def process_custom_product_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await message.answer("Mahsulot nomini kiriting:")
    await state.set_state(AdminState.waiting_for_custom_product_name)

@router.message(AdminState.waiting_for_custom_product_name, F.text)
async def process_custom_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Mahsulot narxini kiriting (raqamlarda, masalan 15000):")
    await state.set_state(AdminState.waiting_for_custom_product_price)

@router.message(AdminState.waiting_for_custom_product_price, F.text)
async def process_custom_product_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Iltimos, faqat raqamlarda kiriting:")
    await state.update_data(price=int(message.text))
    await message.answer("Mahsulot haqida ma'lumot yozib yuboring:")
    await state.set_state(AdminState.waiting_for_custom_product_description)

@router.message(AdminState.waiting_for_custom_product_description, F.text)
async def process_custom_product_description(message: Message, state: FSMContext):
    data = await state.get_data()
    description = message.text
    
    await db.add_custom_product(
        category_id=data['target_category_id'],
        name=data['name'],
        photo_id=data['photo_id'],
        price=data['price'],
        description=description
    )
    
    await message.answer(f"✅ Muvaffaqiyatli qo'shildi!\n\nNomi: {data['name']}\nNarxi: {data['price']} so'm\nM'alumot: {description}")
    await state.clear()

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

# --- SHIRINLIK YOKI TORT O'CHIRISH ---
@router.message(F.text == "🗑 Mahsulot o'chirish")
async def ask_delete_category(message: Message):
    if not await is_admin(message.from_user.id):
        return
    categories = await db.get_categories()
    await message.answer("Nimani o'chirmoqchisiz?", reply_markup=admin_delete_category_inline(categories))

@router.callback_query(F.data == "del_shirinlik")
async def show_delete_product_menu(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    products = await db.get_products()
    if not products:
        return await callback.message.edit_text("O'chirish uchun shirinliklar mavjud emas.")
    from keyboards import admin_delete_products_keyboard
    await callback.message.edit_text("Qaysi birini o'chirmoqchisiz? Tanlang:", reply_markup=admin_delete_products_keyboard(products))
    await callback.answer()

@router.callback_query(F.data == "del_cake_admin")
async def show_delete_cake_menu(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    cakes = await db.get_cakes()
    if not cakes:
        return await callback.message.edit_text("O'chirish uchun tortlar mavjud emas.")
    from keyboards import admin_delete_cakes_keyboard
    await callback.message.edit_text("Qaysi tortni o'chirmoqchisiz? Tanlang:", reply_markup=admin_delete_cakes_keyboard(cakes))
    await callback.answer()

@router.callback_query(F.data.startswith("delcake_"))
async def process_delete_cake(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    cake_id = int(callback.data.split("_")[1])
    await db.delete_cake(cake_id)
    await callback.message.edit_text(callback.message.text + "\n\n✅ Tort o'chirildi.")
    await callback.answer("Tort o'chirildi.")

@router.callback_query(F.data == "del_fastfood_admin")
async def show_delete_fastfood_menu(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    fast_foods = await db.get_fast_foods()
    if not fast_foods:
        return await callback.message.edit_text("O'chirish uchun fast foodlar mavjud emas.")
    from keyboards import admin_delete_fast_foods_keyboard
    await callback.message.edit_text("Qaysi fast foodni o'chirmoqchisiz? Tanlang:", reply_markup=admin_delete_fast_foods_keyboard(fast_foods))
    await callback.answer()

@router.callback_query(F.data.startswith("delfastfood_"))
async def process_delete_fastfood(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return
    fast_food_id = int(callback.data.split("_")[1])
    await db.delete_fast_food(fast_food_id)
    await callback.message.edit_text(callback.message.text + "\n\n✅ Fast food o'chirildi.")
    await callback.answer("Fast food o'chirildi.")

@router.callback_query(F.data.startswith("del_custom_cat_"))
async def show_delete_custom_products_menu(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id): return
    cat_id = int(callback.data.split("_")[3])
    products = await db.get_custom_products(cat_id)
    if not products:
        return await callback.message.edit_text("O'chirish uchun mahsulotlar mavjud emas.")
    from keyboards import admin_delete_custom_products_keyboard
    await callback.message.edit_text("Qaysi mahsulotni o'chirmoqchisiz? Tanlang:", reply_markup=admin_delete_custom_products_keyboard(products))
    await callback.answer()

@router.callback_query(F.data.startswith("delcustomprod_"))
async def process_delete_custom_product(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id): return
    prod_id = int(callback.data.split("_")[1])
    await db.delete_custom_product(prod_id)
    await callback.message.edit_text(callback.message.text + "\n\n✅ Mahsulot o'chirildi.")
    await callback.answer("O'chirildi.")

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

# --- PAYSHANBA SKIDKASI ---
@router.message(F.text == "🎉 Payshanba skidkasi")
async def open_thursday_discount_menu(message: Message):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("Payshanba skidkasi sozlamalari:", reply_markup=thursday_discount_menu())

@router.message(F.text == "🔥 Skidkani yoqish")
async def activate_discount(message: Message):
    if not await is_admin(message.from_user.id):
        return
    await db.set_discount_status(True)
    await message.answer("✅ Skidka muvaffaqiyatli YOQILDI. Mijozlarga arzon narxlar ko'rinishni boshlaydi.")

@router.message(F.text == "⛔️ Skidkani to'xtatish")
async def deactivate_discount(message: Message):
    if not await is_admin(message.from_user.id):
        return
    await db.set_discount_status(False)
    await message.answer("⛔️ Skidka TO'XTATILDI. Barcha narxlar odatdagidek o'z holiga qaytdi.")

@router.message(F.text == "🎂 Tortlarga skidka qilish")
async def show_discount_cakes(message: Message):
    if not await is_admin(message.from_user.id):
        return
    cakes = await db.get_cakes()
    if not cakes:
        return await message.answer("Menyuda tortlar yo'q.")
    await message.answer("Qaysi tort uchun skidka miqdorini kiritmoqchisiz?", reply_markup=admin_discount_cakes_keyboard(cakes))

@router.callback_query(F.data.startswith("disccake_"))
async def ask_cake_discount_amount(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return
    cake_id = int(callback.data.split("_")[1])
    cake = await db.get_cake(cake_id)
    await state.update_data(discount_target_id=cake_id)
    await state.set_state(AdminState.waiting_for_cake_discount_amount)
    
    await callback.message.edit_text(f"🎂 {cake['name']}\nJoriy narxi: {cake['price']}\n\nSkidka summasini kiriting (raqamlarda).\nAgar skidka qilinmasligi kerak bo'lsa 0 deb yuboring:")
    await callback.answer()

@router.message(AdminState.waiting_for_cake_discount_amount, F.text)
async def process_cake_discount_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Iltimos, faqat raqamlarda kiriting:")
        
    amount = int(message.text)
    data = await state.get_data()
    cake_id = data['discount_target_id']
    
    await db.update_cake_discount(cake_id, amount)
    
    cakes = await db.get_cakes()
    text = "✅ Muvaffaqiyatli chegirma summasi belgilandi.\n\nQolgan tortlarni skidka qilish uchun yana tanlang:"
    from keyboards import admin_discount_cakes_keyboard
    await message.answer(text, reply_markup=admin_discount_cakes_keyboard(cakes))
    await state.clear()

@router.message(F.text == "🍔 Fast foodlarga skidka qilish")
async def show_discount_fastfoods(message: Message):
    if not await is_admin(message.from_user.id):
        return
    fast_foods = await db.get_fast_foods()
    if not fast_foods:
        return await message.answer("Menyuda fast foodlar yo'q.")
    from keyboards import admin_discount_fast_foods_keyboard
    await message.answer("Qaysi fast food uchun skidka miqdorini kiritmoqchisiz?", reply_markup=admin_discount_fast_foods_keyboard(fast_foods))

@router.callback_query(F.data.startswith("discfastfood_"))
async def ask_fastfood_discount_amount(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return
    ff_id = int(callback.data.split("_")[1])
    ff = await db.get_fast_food(ff_id)
    await state.update_data(discount_target_id=ff_id)
    await state.set_state(AdminState.waiting_for_fast_food_discount_amount)
    
    await callback.message.edit_text(f"🍔 {ff['name']}\nJoriy narxi: {ff['price']}\n\nSkidka summasini kiriting (raqamlarda).\nAgar skidka qilinmasligi kerak bo'lsa 0 deb yuboring:")
    await callback.answer()

@router.message(AdminState.waiting_for_fast_food_discount_amount, F.text)
async def process_fastfood_discount_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Iltimos, faqat raqamlarda kiriting:")
        
    amount = int(message.text)
    data = await state.get_data()
    ff_id = data['discount_target_id']
    
    await db.update_fast_food_discount(ff_id, amount)
    
    fast_foods = await db.get_fast_foods()
    text = "✅ Muvaffaqiyatli chegirma summasi belgilandi.\n\nQolgan fast foodlarni skidka qilish uchun yana tanlang:"
    from keyboards import admin_discount_fast_foods_keyboard
    await message.answer(text, reply_markup=admin_discount_fast_foods_keyboard(fast_foods))
    await state.clear()

@router.message(F.text == "🍰 Shirinliklarga skidka qilish")
async def show_discount_products(message: Message):
    if not await is_admin(message.from_user.id):
        return
    products = await db.get_products()
    if not products:
        return await message.answer("Menyuda shirinliklar yo'q.")
    await message.answer("Qaysi shirinlik uchun skidka kiritmoqchisiz?", reply_markup=admin_discount_products_keyboard(products))

@router.callback_query(F.data.startswith("discproduct_"))
async def ask_product_discount_whole(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return
    product_id = int(callback.data.split("_")[1])
    product = await db.get_product(product_id)
    await state.update_data(discount_target_id=product_id)
    await state.set_state(AdminState.waiting_for_product_discount_whole)
    
    await callback.message.edit_text(f"🍰 {product['name']}\nButunicha narxi: {product['price_whole']}\nKusok narxi: {product['price_slice']}\n\nButunicha uchun skidka summasini kiriting (raqamlarda).\nAgar butuniga skidka bo'lmasa 0 kiriting:")
    await callback.answer()

@router.message(AdminState.waiting_for_product_discount_whole, F.text)
async def process_product_discount_whole(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Iltimos, faqat raqamlarda kiriting:")
        
    amount = int(message.text)
    await state.update_data(discount_whole=amount)
    await state.set_state(AdminState.waiting_for_product_discount_slice)
    
    await message.answer("Endi ushbu shirinlikning KUSOK qismi uchun skidka summasini kiriting (raqamlarda).\nAgar kusok uchun skidka bo'lmasa 0 kiriting:")

@router.message(AdminState.waiting_for_product_discount_slice, F.text)
async def process_product_discount_slice(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Iltimos, faqat raqamlarda kiriting:")
        
    discount_slice = int(message.text)
    data = await state.get_data()
    product_id = data['discount_target_id']
    discount_whole = data['discount_whole']
    
    await db.update_product_discount(product_id, discount_whole, discount_slice)
    
    products = await db.get_products()
    text = "✅ Muvaffaqiyatli chegirma belgilandi.\n\nQolgan shirinliklarni skidka qilish uchun yana tanlang:"
    from keyboards import admin_discount_products_keyboard
    await message.answer(text, reply_markup=admin_discount_products_keyboard(products))
    await state.clear()

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

# --- CUSTOM ORDER PRICE SETUP ---
@router.callback_query(F.data.startswith("admin_set_price_"))
async def ask_custom_order_price(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return
    order_id = int(callback.data.split("_")[3])
    await callback.message.answer(f"Buyurtma #{order_id} uchun summani kiriting (raqamlarda):")
    await state.update_data(set_price_order_id=order_id)
    await state.set_state(AdminState.waiting_for_custom_order_price)
    await callback.answer()

@router.message(AdminState.waiting_for_custom_order_price, F.text)
async def process_custom_order_price(message: Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit():
        await message.answer("Iltimos, summani faqat raqamlarda kiriting:")
        return
        
    data = await state.get_data()
    order_id = data.get('set_price_order_id')
    price = int(message.text)
    
    await db.update_order_price(order_id, price)
    order = await db.get_order(order_id)
    
    from keyboards import checkout_keyboard
    try:
        await bot.send_message(
            chat_id=order['user_id'],
            text=f"✅ Buyurtma #{order_id} uchun narx belgilandi: {price} so'm.\n\nPastdagi to'lov qilish tugmasi orqali to'lovni amalga oshirishingiz mumkin:",
            reply_markup=checkout_keyboard(order_id)
        )
        await message.answer(f"✅ Summa mijozga muvaffaqiyatli yuborildi ({price} so'm).")
    except Exception as e:
        await message.answer("Xatolik: Mijozga xabar yuborib bo'lmadi.")
        print(e)
    
    await state.clear()
