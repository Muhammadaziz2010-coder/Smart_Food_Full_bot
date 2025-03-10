from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram import Router, types, F
from aiogram.filters import Command
from sqlalchemy.util import await_fallback

from keyboards.keyboard import *
from utils.utils import *
from database.database import SessionLocal, User, Order, Discount
from geopy.geocoders import Nominatim
import re
import logging

router = Router()

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot_errors.log'
)

ADMIN_ID = "6447578381"

def go_back_one_step(user, session):
    step_order = ["start", "phone_number", "menu", "ask_location", "location", "orders", "discounts", "location_saved", "type_of_orders", "web_app", "developer"]
    if user.step in step_order:
        prev_index = max(0, step_order.index(user.step) - 1)
        user.step = step_order[prev_index]
        session.commit()

def get_reply_markup_for_step(step):
    step_keyboards = {
        "menu": menu_keys,
        "ask_location": location_keyboard,
        "location": main,
        "orders": menu_keys,
        "discounts": menu_keys,
        "location_saved": validate_location,
        "web_app": main,
        "developer": menu_keys,
    }
    return step_keyboards.get(step, menu_keys)

async def send_error_to_admin(message: Message, error_message):
    try:
        await message.bot.send_message(ADMIN_ID, f"Botda xatolik:\n{error_message}")
    except Exception as e:
        logging.error(f"Failed to send error to admin: {e}")

async def notify_admin_new_user(message: Message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Username yo‘q"
        full_name = message.from_user.full_name or "Ism yo‘q"
        await message.bot.send_message(
            ADMIN_ID,
                f"📢 *Yangi foydalanuvchi botga kirdi!*\n\n"
                f"🆔 ID: {user_id}\n"
                f"👤 Username: @{username}\n"
                f"📛 Ism: {full_name}"
        )
    except Exception as e:
        logging.error(f"Failed to notify admin about new user: {e}")

class States(StatesGroup):
    phone = State()
    manual_address = State()

# Command Handlers
@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    username = message.from_user.username
    name = message.from_user.full_name

    with SessionLocal() as session:
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                if user.phone_number:
                    await message.answer("🍽 Menuga xush kelibsiz!", reply_markup=menu_keys)
                else:
                    await state.set_state(States.phone)
                    await message.answer("📞 Iltimos, telefon raqamingizni yuboring:", reply_markup=keyboard)
            else:
                await notify_admin_new_user(message)
                await state.set_state(States.phone)
                add_user(telegram_id, username, name, step="phone_number")
                await message.answer("📞 Iltimos, telefon raqamingizni yuboring:", reply_markup=keyboard)
        except Exception as e:
            error_msg = f"Error in start_command: {str(e)}"
            logging.error(error_msg)
            await send_error_to_admin(message, error_msg)
            await message.answer("⚠️ Xatolik yuz berdi, qayta urinib ko‘ring.")

@router.message(States.phone)
async def handle_phone_number(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    phone_number = None

    # Telefon raqamini olish
    if message.contact:
        phone_number = message.contact.phone_number
    elif message.text:
        # Faqat raqamlar va '+' belgisini qoldirish uchun tozalash
        phone_number = re.sub(r"[^\d+]", "", message.text)

    with SessionLocal() as session:
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
                return

            if not phone_number or user.step != "phone_number":
                await message.answer("⚠️ Iltimos, telefon raqamingizni to‘g‘ri kiriting yoki kontakt yuboring.")
                return

            # Telefon raqamini tekshirish
            digit_count = len(re.sub(r"\+", "", phone_number))
            if digit_count == 12 and phone_number.startswith("+998") and re.fullmatch(r"\+998\d{9}", phone_number):
                # 12 raqamli va +998 bilan boshlansa
                user.phone_number = phone_number
            elif digit_count == 9 and re.fullmatch(r"\d{9}", phone_number):
                # 9 raqamli bo‘lsa, +998 qo‘shiladi
                phone_number = f"+998{phone_number}"
                user.phone_number = phone_number
            else:
                await message.answer("⚠️ Telefon raqami noto‘g‘ri! 9 raqamli (masalan, 901234567) yoki +998 bilan 12 raqamli (masalan, +998901234567) bo‘lishi kerak.")
                return

            user.step = "menu"
            session.commit()
            await state.clear()
            await message.answer("🍽 Menuga xush kelibsiz!", reply_markup=menu_keys)
        except Exception as e:
            error_msg = f"Error in handle_phone_number: {str(e)}"
            logging.error(error_msg)
            await send_error_to_admin(message, error_msg)
            await message.answer("⚠️ Xatolik yuz berdi, qayta urinib ko‘ring.")

@router.message(F.text == "🛒 Buyurtma Berish")
async def handle_order(message: Message):
    with SessionLocal() as session:
        try:
            telegram_id = message.from_user.id
            user = session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
                return

            user.step = "type_of_orders"
            session.commit()
            await message.answer("🔎 Iltimos, Buyurtma turini tanlang.", reply_markup=main)
        except Exception as e:
            error_msg = f"Error in handle_order: {str(e)}"
            logging.error(error_msg)
            await send_error_to_admin(message, error_msg)
            await message.answer("⚠️ Xatolik yuz berdi.")

@router.message(F.text == "🚚 Yetkazib berish")
async def handle_delivery(message: Message):
    with SessionLocal() as session:
        try:
            telegram_id = message.from_user.id
            user = session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
                return

            user.type_of_orders = "Yetkazib berish"
            user.step = "ask_location"
            session.commit()
            await message.answer("📍 Iltimos, Manzilingizni yuboring.", reply_markup=location_keyboard)
        except Exception as e:
            error_msg = f"Error in handle_delivery: {str(e)}"
            logging.error(error_msg)
            await send_error_to_admin(message, error_msg)
            await message.answer("⚠️ Xatolik yuz berdi.")

@router.message(F.text == "📦 Olib ketish")
async def handle_pickup(message: Message):
    with SessionLocal() as session:
        try:
            telegram_id = message.from_user.id
            user = session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
                return

            user.type_of_orders = "Olib ketish"
            user.step = "web_app"
            session.commit()
            await message.answer("📱 Web ilovaga o‘tishingiz mumkin.", reply_markup=web_app_keyboard)
        except Exception as e:
            error_msg = f"Error in handle_pickup: {str(e)}"
            logging.error(error_msg)
            await send_error_to_admin(message, error_msg)
            await message.answer("⚠️ Xatolik yuz berdi.")

@router.message(F.text == "🛍️ Mening buyurtmalarim")
async def my_orders(message: Message):
    with (SessionLocal() as session):
        try:
            telegram_id = message.from_user.id
            user = session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
                return

            user.step = "orders"
            session.commit()
            orders = session.query(Order).filter_by(user_id=user.id).all()

            if orders:
                response_text = "📦 Sizning buyurtmalaringiz:\n\n"
                for order in orders:
                    response_text +=f'🆔 Buyurtma ID: {order.id}\n'                        f'📅 Sana: {order.date}\n'                        f'📍 Manzil: {order.address or 'Noma\'lum'}\n'                        f'💰 Narx: {order.total_price or 0} so`m\n'                        f'📜 Holat: {order.status or 'Holat mavjud emas'}\n'                        "----------------------\n"
                    await message.answer(response_text, reply_markup=menu_keys)
            else:
                await message.answer("❌ Sizda hali buyurtmalar mavjud emas.", reply_markup=menu_keys)
        except Exception as e:
            error_msg = f"Error in my_orders: {str(e)}"
            logging.error(error_msg)
            await send_error_to_admin(message, error_msg)
            await message.answer("⚠️ Xatolik yuz berdi.")

@router.message(F.text == "💰 Aksiyalar")
async def handle_discounts(message: Message):
    with SessionLocal() as session:
        try:
            telegram_id = message.from_user.id
            user = session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
                return

            user.step = "discounts"
            session.commit()
            discounts = session.query(Discount).all()

            if discounts:
                response_text = "🎉 Mavjud aksiyalar:\n\n"
                for discount in discounts:
                    response_text += (
                        f'🔹 {discount.title}\n'
                        f'📜 {discount.description}\n'
                        f'💰 Chegirma: {discount.discount_percent}%\n'
                        '----------------------\n'
                    )
                await message.answer(response_text, reply_markup=menu_keys)
            else:
                await message.answer("❌ Hozircha hech qanday aksiya mavjud emas.", reply_markup=menu_keys)
        except Exception as e:
            error_msg = f"Error in handle_discounts: {str(e)}"
            logging.error(error_msg)
            await send_error_to_admin(message, error_msg)
            await message.answer("⚠️ Xatolik yuz berdi.")

@router.message(F.text == "👈 Ortga")
async def handle_back(message: Message):
    with SessionLocal() as session:
        try:
            telegram_id = message.from_user.id
            user = session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
                return

            if user.step in ["type_of_orders", "ask_location", "location", "location_saved", "web_app", "developer"]:
                user.step = "menu"
            else:
                go_back_one_step(user, session)

            session.commit()
            await message.answer("⬅️ Orqaga qaytdik!", reply_markup=menu_keys)
        except Exception as e:
            error_msg = f"Error in handle_back: {str(e)}"
            logging.error(error_msg)
            await send_error_to_admin(message, error_msg)
            await message.answer("⚠️ Xatolik yuz berdi.")

@router.message(F.location)
async def handle_location(message: Message):
    with SessionLocal() as session:
        try:
            telegram_id = message.from_user.id
            user = session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user or user.step != "ask_location":
                await message.answer("⚠️ Lokatsiya noto‘g‘ri vaqtda yuborildi.")
                return

            latitude = message.location.latitude
            longitude = message.location.longitude
            geolocator = Nominatim(user_agent="telegram_bot")
            location = geolocator.reverse((latitude, longitude))
            address = location.address if location and location.address else "Noma'lum"

            user.latitude = latitude
            user.longitude = longitude
            user.location = address
            user.step = "location_saved"
            session.commit()

            await message.answer(f'📍 Sizning manzilingiz: {address}', reply_markup=validate_location)
            await message.answer("‼️ Agar manzilingiz to‘g‘ri bo‘lsa, tasdiqlang yoki qayta yuboring.")
        except Exception as e:
            error_msg = f'Error in handle_location: {str(e)}'
            logging.error(error_msg)
            await send_error_to_admin(message, error_msg)
            await message.answer("⚠️ Manzilni qayta ishlashda xatolik.")

@router.message(F.text == "🔄 Manzilni qayta jo‘natish")
async def handle_manual_address_prompt(message: Message, state: FSMContext):
    with SessionLocal() as session:
        try:
            telegram_id = message.from_user.id
            user = session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
                return

            await state.set_state(States.manual_address)
            await message.answer("📍 Iltimos, manzilingizni qo‘lda kiriting (masalan: Toshkent, Chilanzar, 45-uy):")
        except Exception as e:
            error_msg = f'Error in handle_manual_address_prompt: {str(e)}'
            logging.error(error_msg)
            await send_error_to_admin(message, error_msg)
            await message.answer("⚠️ Xatolik yuz berdi.")

@router.message(States.manual_address)
async def process_manual_address(message: Message, state: FSMContext):
    with SessionLocal() as session:
        try:
            telegram_id = message.from_user.id
            user = session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
                return

            address = message.text.strip()
            if len(address) < 5:
                await message.answer("⚠️ Manzil juda qisqa, iltimos batafsil yozing.")
                return

            geolocator = Nominatim(user_agent="telegram_bot")
            location = geolocator.geocode(address)

            if not location:
                await message.answer("⚠️ Manzil topilmadi, iltimos aniqroq yozing.")
                return

            user.latitude = location.latitude
            user.longitude = location.longitude
            user.location = address
            user.step = "web_app"
            session.commit()
            await state.clear()
            await message.answer("✅ Manzilingiz saqlandi! Tasdiqlang yoki qayta yuboring.", reply_markup=web_app_keyboard)
        except Exception as e:
            error_msg = f'Error in process_manual_address: {str(e)}'
            logging.error(error_msg)
            await send_error_to_admin(message, error_msg)
            await message.answer("⚠️ Xatolik yuz berdi.")

@router.message(F.text == "✅ Tasdiqlash")
async def confirm_location(message: Message):
    with SessionLocal() as session:
        try:
            telegram_id = message.from_user.id
            user = session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user or user.step != "location_saved":
                await message.answer("⚠️ Avval manzilingizni yuboring!")
                return

            user.step = "web_app"
            session.commit()
            await message.answer("✅ Manzil tasdiqlandi! Web ilovaga o‘tishingiz mumkin.", reply_markup=web_app_keyboard)
        except Exception as e:
            error_msg = f'Error in confirm_location: {str(e)}'
            logging.error(error_msg)
            await send_error_to_admin(message, error_msg)
            await message.answer("⚠️ Xatolik yuz berdi.")

@router.message(F.text == "💻 Dasturchi bilan bog`lanish")
async def return_developer(message: Message):
    with SessionLocal() as session:
        try:
            telegram_id = message.from_user.id
            user = session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                await message.answer("⚠️ Xatolik: Avval /start ni bosing.")
                return

            user.step = "developer"
            session.commit()

            developer_info = (
                "👨‍💻 Dasturchi:\n"
                "📝 Ism: Dasturchi Ismi\n"
                "📞 Tel: +998 90 123 45 67\n"
                "💬 Telegram: @dasturchi_username\n"
            )
            await message.answer(developer_info, reply_markup=menu_keys, parse_mode="HTML")
        except Exception as e:
            error_msg = f'Error in return_developer: {str(e)}'
            logging.error(error_msg)
            await send_error_to_admin(message, error_msg)
            await message.answer("⚠️ Xatolik yuz berdi.")

@router.message()
async def fallback_handler(message: Message):
    try:
        telegram_id = message.from_user.id
        with SessionLocal() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                await message.answer("Menyuga xush kelibsiz!", reply_markup=menu_keys)
            else:
                await message.answer("Iltimos, avval /start buyrug‘ini ishlatib botni boshlang.")
            user.step = "menu"
            session.commit()
    except Exception as e:
        error_msg = f'Error in fallback_handler: {str(e)}'
        logging.error(error_msg)
        await send_error_to_admin(message, error_msg)