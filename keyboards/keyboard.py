from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from aiogram.types.web_app_info import WebAppInfo
keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📱 Iltimos Telefon raqamni yuboring", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
menu_keys = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🛒 Buyurtma Berish"), KeyboardButton(text="🛍️ Mening buyurtmalarim")],
                [KeyboardButton(text="💰 Aksiyalar"), KeyboardButton(text="💻 Dasturchi bilan bog`lanish")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

location_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Lokatsiyamni yuborish", request_location=True)],
        [KeyboardButton(text="👈 Ortga")],

    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

web_app_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Web app ni ochish", web_app=WebAppInfo(url="https://269f-185-213-230-75.ngrok-free.app/"))],
        [KeyboardButton(text="❌ Bekor qilish")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

validate_location = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔄 Manzilni qayta jo‘natish"), KeyboardButton(text="✅ Tasdiqlash")],
        [KeyboardButton(text="👈 Ortga")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚚 Yetkazib berish"), KeyboardButton(text="📦 Olib ketish")],
        [KeyboardButton(text="👈 Ortga")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)