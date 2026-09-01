from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamni yuborish tugmasi"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return kb


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Ro'yxatdan o'tgan foydalanuvchilar uchun qulay asosiy menyu"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📍 Bizning lokatsiya"),
                KeyboardButton(text="📞 Biz bilan bog'lanish")
            ],
            [
                KeyboardButton(text="ℹ️ Biz haqimizda")
            ]
        ],
        resize_keyboard=True
    )
    return kb


def remove_keyboard() -> ReplyKeyboardRemove:
    """Tugmalarni olib tashlash"""
    return ReplyKeyboardRemove()
