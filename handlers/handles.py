from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram import Router
from aiogram.filters import Command
from keyboards.keyboard import *
from utils.utils import *
from database.database import SessionLocal, User, Order, Discount

router = Router()

def go_back_one_step(user, session):
    step_order = ["start", "phone_number", "ask_real_name", "menu", "ask_location", "location", "orders", "discounts"]
    if user.step in step_order:
        prev_index = max(0, step_order.index(user.step) - 1)
        user.step = step_order[prev_index]
        session.commit()

def get_reply_markup_for_step(step):
    if step == "menu":
        return menu_keys
    elif step == "ask_location":
        return location_keyboard
    elif step == "location":
        return web_app_keyboard
    elif step == "orders":
        return menu_keys
    elif step == "discounts":
        return menu_keys
    else:
        return keyboard

@router.message(Command("start"))
async def start_command(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    name = message.from_user.full_name

    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if user:
        await message.answer("🍽 Menuga xush kelibsiz!", reply_markup=menu_keys)
    else:
        add_user(telegram_id, username, name, step="phone_number")  # ✨ name argumenti qo‘shildi
        await message.answer(
            "👋 Assalomu alaykum! \n"
            "🤖 Men Smart Food botman! \n\n"
            "📞 Iltimos, telefon raqamingizni yuboring:",
            reply_markup=keyboard
        )
    session.close()


@router.message(lambda message: message.contact)
async def handle_phone_number(message: Message):
    telegram_id = message.from_user.id
    phone_number = message.contact.phone_number

    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if user:
        if phone_number:
            # Telefon raqami kiritilgan bo'lsa
            user.phone_number = phone_number
            user.step = "ask_real_name"
            session.commit()
            await message.answer("✍️ Iltimos, to‘liq ismingizni kiriting (Real ismingiz):", reply_markup=None)
        else:
            await message.answer("⚠️ Telefon raqamingizni yuborishingiz shart!")
    else:
        await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
    session.close()


@router.message(lambda message: message.text and message.text.isalpha())
async def handle_real_name(message: Message):
    telegram_id = message.from_user.id
    real_name = message.text.strip()

    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if user and user.step == "ask_real_name":
        if real_name:  # Real ism kiritilgan bo'lsa
            user.real_name = real_name
            user.step = "menu"
            session.commit()
            await message.answer(
                f"✅ Rahmat, {real_name}! Ma'lumotlaringiz saqlandi. \n\n"
                f"🆔 ID: {user.id}\n"
                f"👤 Ism: {user.real_name}\n"
                f"🏷️ Username: {user.username}\n"
                f"📞 Telefon: {user.phone_number}\n\n"
                "🎉 Smart Food botga xush kelibsiz!",
                reply_markup=menu_keys
            )
        else:
            await message.answer("⚠️ Xatolik: To‘liq ismni kiriting.")
    else:
        await message.answer("⚠️ Xatolik: Avval telefon raqamingizni yuboring.")
    session.close()

@router.message(lambda message: message.text == "🛒 Buyurtma Berish")
async def handle_order(message: Message):
    session = SessionLocal()
    telegram_id = message.from_user.id
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        user.step = "ask_location"
        session.commit()
        await message.answer("📝 Buyurtma berish bo'limiga xush kelibsiz!\n\n"
                             "📍 Iltimos, Manzilingizni yuboring.", reply_markup=location_keyboard)
    else:
        await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
    session.close()

@router.message(lambda message: message.text == "👈 Ortga")
async def handle_back(message: Message):
    session = SessionLocal()
    telegram_id = message.from_user.id
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if user:
        go_back_one_step(user, session)
        await message.answer("⬅️ Orqaga qaytdik!", reply_markup=get_reply_markup_for_step(user.step))
    else:
        await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
    session.close()

@router.message(lambda message: message.location)
async def handle_location(message: Message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    telegram_id = message.from_user.id

    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if user:
        user.latitude = latitude
        user.longitude = longitude
        user.step = "location"
        session.commit()
        await message.answer("🌍 Rahmat! Lokatsiyangiz saqlandi! \n"
                             "🛒 Buyurtma berish uchun pastdagi tugmani bosing", reply_markup=web_app_keyboard)
    else:
        await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
    session.close()

@router.message(lambda message: message.text == "🛍️ Mening buyurtmalarim")
async def my_orders(message: Message):
    session = SessionLocal()
    telegram_id = message.from_user.id
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if user:
        user.step = "orders"
        session.commit()
        orders = session.query(Order).filter_by(user_id=user.id).all()
        if orders:
            response_text = "📦 Sizning buyurtmalaringiz:\n\n"
            for order in orders:
                response_text += (
                    f"🆔 Buyurtma ID: {order.id}\n"
                    f"📅 Sana: {order.date}\n"
                    f"📍 Manzil: {order.address or 'Noma\'lum'}\n"
                    f"💰 Narx: {order.total_price or 0} so'm\n"
                    f"📜 Holat: {order.status or 'Holat mavjud emas'}\n"
                    "----------------------\n"
                )
            await message.answer(response_text, reply_markup=menu_keys)
        else:
            await message.answer("❌ Sizda hali buyurtmalar mavjud emas.", reply_markup=menu_keys)
    else:
        await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
    session.close()
