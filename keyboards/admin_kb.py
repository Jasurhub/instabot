from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin boshqaruv menyusi klaviaturasi"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
                InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin_broadcast"),
            ],
            [
                InlineKeyboardButton(text="📍 Lokatsiyani sozlash", callback_data="admin_location_menu"),
                InlineKeyboardButton(text="💾 Bazani yuklab olish", callback_data="admin_backup"),
            ],
            [
                InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin_refresh"),
            ]
        ]
    )
    return kb


def get_location_menu_keyboard() -> InlineKeyboardMarkup:
    """Lokatsiya boshqaruv menyusi klaviaturasi"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👀 Joriy lokatsiyani ko'rish", callback_data="admin_view_loc"),
            ],
            [
                InlineKeyboardButton(text="✏️ Yangi lokatsiya o'rnatish", callback_data="admin_set_loc"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back"),
            ]
        ]
    )
    return kb


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Xabar yuborishni bekor qilish tugmasi"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel")
            ]
        ]
    )
    return kb
