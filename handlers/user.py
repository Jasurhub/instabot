import logging
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import config
from database import Database
from states import RegistrationState
from keyboards import get_phone_keyboard, get_main_menu_keyboard, remove_keyboard
from utils import validate_full_name, validate_phone_number

logger = logging.getLogger(__name__)
user_router = Router()
db = Database(config.db_path)


@user_router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    """
    /start komandasi qabul qilinganda (UTM manbasi bilan birga)
    """
    await state.clear()
    user = message.from_user
    username = user.username if user else None
    user_id = user.id if user else message.chat.id

    # Deep linking (Instagram/reklama manbasi: ?start=reels, ?start=bio, etc.)
    source = command.args.strip() if command.args else "direct"
    await state.update_data(source=source)

    # Bazadan tekshiramiz: foydalanuvchi avval ro'yxatdan o'tganmi?
    existing_user = await db.get_user(user_id)
    if existing_user and existing_user.get("phone_number") and existing_user.get("full_name"):
        full_name = existing_user["full_name"]
        
        loc = await db.get_location()
        lat = loc["latitude"] if loc else config.location_latitude
        lon = loc["longitude"] if loc else config.location_longitude
        title = loc["title"] if loc else config.location_title
        address = loc["address"] if loc else config.location_address

        welcome_back_text = (
            f"👋 <b>Assalomu alaykum, {full_name}!</b>\n\n"
            f"✅ <b>Siz allaqachon muvaffaqiyatli ro'yxatdan o'tgansiz.</b>\n\n"
            f"ℹ️ <b>Biz haqimizda:</b>\n{config.about_me}\n\n"
            f"📍 <b>Bizning bino lokatsiyasi quyida yuborildi:</b>"
        )

        await message.answer(
            text=welcome_back_text,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )

        try:
            await message.answer_location(
                latitude=lat,
                longitude=lon
            )
            await message.answer(
                f"🏢 <b>{title}</b>\n"
                f"📍 <b>Manzil:</b> {address}\n\n"
                f"Savollaringiz bo'lsa pastdagi menyu orqali biz bilan bog'lanishingiz mumkin.",
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard()
            )
        except Exception as e:
            logger.error(f"Lokatsiya yuborishda xatolik: {e}")
            await message.answer(
                f"🏢 <b>{title}</b>\n"
                f"📍 <b>Manzil:</b> {address}",
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard()
            )
        return

    # Yangi foydalanuvchi — bazaga /start bosganini qayd qilish
    await db.register_start_user(user_id=user_id, username=username, source=source)

    welcome_text = (
        f"👋 <b>Assalomu alaykum, {user.first_name if user else ''}!</b>\n\n"
        f"ℹ️ <b>Biz haqimizda:</b>\n{config.about_me}\n\n"
        f"🤖 <b>Bot haqida:</b>\n{config.about_bot}\n\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"📍 <b>Bino lokatsiyasini olish uchun iltimos, ro'yxatdan o'ting.</b>\n\n"
        f"✍️ <b>Ism va Familiyangizni kiriting:</b>\n"
        f"<i>(Masalan: Jasur Xolboyev)</i>"
    )

    await message.answer(
        text=welcome_text,
        parse_mode="HTML",
        reply_markup=remove_keyboard()
    )
    await state.set_state(RegistrationState.waiting_for_fullname)


@user_router.message(RegistrationState.waiting_for_fullname, F.text)
async def process_fullname(message: Message, state: FSMContext):
    """
    Ism va familiyani tekshirish va qabul qilish
    """
    is_valid, result = validate_full_name(message.text)

    if not is_valid:
        await message.answer(
            f"⚠️ <b>Xatolik:</b> {result}\n\n"
            f"Iltimos, ism va familiyangizni to'g'ri ko'rinishda qayta kiriting:\n"
            f"<i>(Masalan: Jasur Xolboyev)</i>",
            parse_mode="HTML"
        )
        return

    formatted_name = result
    await state.update_data(full_name=formatted_name)

    prompt_phone = (
        f"✅ Rahmat, <b>{formatted_name}</b>!\n\n"
        f"📱 Endi telefon raqamingizni yuboring.\n"
        f"Pastdagi <b>«📱 Telefon raqamni yuborish»</b> tugmasini bosing yoki raqamingizni yozing:\n"
        f"<i>(Masalan: +998901234567)</i>"
    )

    await message.answer(
        text=prompt_phone,
        parse_mode="HTML",
        reply_markup=get_phone_keyboard()
    )
    await state.set_state(RegistrationState.waiting_for_phone)


@user_router.message(RegistrationState.waiting_for_fullname)
async def process_fullname_invalid_content(message: Message):
    """Foydalanuvchi matn o'rniga boshqa narsa yuborsa"""
    await message.answer(
        "⚠️ Iltimos, ism va familiyangizni <b>matn shaklida</b> yozib yuboring.\n"
        "<i>(Masalan: Jasur Xolboyev)</i>",
        parse_mode="HTML"
    )


@user_router.message(RegistrationState.waiting_for_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext, bot: Bot):
    """Foydalanuvchi kontakt tugmasi orqali raqam yuborganda"""
    contact = message.contact
    if not contact:
        await message.answer("⚠️ Kontakt ma'lumoti topilmadi. Iltimos qaytadan urinib ko'ring.")
        return

    phone_number = contact.phone_number
    if not phone_number.startswith("+"):
        phone_number = f"+{phone_number}"

    await finalize_registration(
        message=message,
        state=state,
        bot=bot,
        phone_number=phone_number
    )


@user_router.message(RegistrationState.waiting_for_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext, bot: Bot):
    """Foydalanuvchi telefon raqamini matn sifatida yozganda"""
    is_valid, result = validate_phone_number(message.text)

    if not is_valid:
        await message.answer(
            f"⚠️ <b>Xatolik:</b> {result}\n\n"
            f"Iltimos, pastdagi <b>«📱 Telefon raqamni yuborish»</b> tugmasini bosing yoki raqamni to'g'ri formatda kiriting:\n"
            f"<i>(Masalan: +998901234567)</i>",
            parse_mode="HTML",
            reply_markup=get_phone_keyboard()
        )
        return

    phone_number = result
    await finalize_registration(
        message=message,
        state=state,
        bot=bot,
        phone_number=phone_number
    )


async def finalize_registration(
    message: Message,
    state: FSMContext,
    bot: Bot,
    phone_number: str
):
    """Ro'yxatdan o'tishni yakunlash, bazaga yozish, kanalga yuborish va lokatsiyani jo'natish"""
    data = await state.get_data()
    full_name = data.get("full_name", "Noma'lum")
    source = data.get("source", "direct")
    user = message.from_user
    username = user.username if user else None
    user_id = user.id if user else message.chat.id

    # Bazaga to'liq saqlash
    await db.add_or_update_user(
        user_id=user_id,
        full_name=full_name,
        phone_number=phone_number,
        username=username,
        source=source
    )
    await state.clear()

    # Muvaffaqiyat xabari
    success_text = (
        f"🎉 <b>Tabriklaymiz, ro'yxatdan muvaffaqiyatli o'tdingiz!</b>\n\n"
        f"👤 <b>Ism-familiya:</b> {full_name}\n"
        f"📱 <b>Telefon:</b> {phone_number}\n\n"
        f"📍 <b>Bizning bino lokatsiyasi quyida yuborilmoqda:</b>"
    )

    await message.answer(
        text=success_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )

    # Lokatsiyani bazadan olish
    loc = await db.get_location()
    lat = loc["latitude"] if loc else config.location_latitude
    lon = loc["longitude"] if loc else config.location_longitude
    title = loc["title"] if loc else config.location_title
    address = loc["address"] if loc else config.location_address

    # Lokatsiyani yuborish
    try:
        await message.answer_location(
            latitude=lat,
            longitude=lon
        )
        await message.answer(
            f"🏢 <b>{title}</b>\n"
            f"📍 <b>Manzil:</b> {address}\n\n"
            f"Sizni kutib qolamiz! Savollaringiz bo'lsa biz bilan bog'lanishingiz mumkin.",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Lokatsiya yuborishda xatolik: {e}")
        await message.answer(
            f"🏢 <b>{title}</b>\n"
            f"📍 <b>Manzil:</b> {address}",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )

    # Telegram kanalga hisobot yuborish
    if config.channel_id and str(config.channel_id) != "0":
        try:
            now_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            username_display = f"@{username}" if username else "<i>Mavjud emas</i>"
            source_display = f"#{source}" if source != "direct" else "To'g'ridan-to'g'ri (Direct)"

            channel_report = (
                "⚡️ <b>YANGI LEAD (FOYDALANUVCHI) RO'YXATDAN O'TDI!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>Ism-familiya:</b> {full_name}\n"
                f"📱 <b>Telefon raqam:</b> <code>{phone_number}</code>\n"
                f"🌐 <b>Username:</b> {username_display}\n"
                f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n"
                f"🏷 <b>Manba (UTM):</b> {source_display}\n"
                f"📅 <b>Ro'yxat vaqti:</b> {now_str}\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "📌 <i>Ushbu ma'lumot Instagram bot orqali qabul qilindi.</i>"
            )

            await bot.send_message(
                chat_id=config.channel_id,
                text=channel_report,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Kanalga hisobot yuborishda xatolik ({config.channel_id}): {e}")


# ==================== DOIMIY FOYDALANUVCHI MENYUSI ====================

@user_router.message(F.text == "📍 Bizning lokatsiya")
async def user_menu_location(message: Message):
    """Foydalanuvchi istalgan vaqt lokatsiyani qayta ko'rishi"""
    loc = await db.get_location()
    lat = loc["latitude"] if loc else config.location_latitude
    lon = loc["longitude"] if loc else config.location_longitude
    title = loc["title"] if loc else config.location_title
    address = loc["address"] if loc else config.location_address

    try:
        await message.answer_location(latitude=lat, longitude=lon)
        await message.answer(
            f"🏢 <b>{title}</b>\n"
            f"📍 <b>Manzil:</b> {address}\n\n"
            f"Sizni ofisimizda kutib qolamiz!",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Lokatsiya xatolik: {e}")
        await message.answer(
            f"🏢 <b>{title}</b>\n📍 <b>Manzil:</b> {address}",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )


@user_router.message(F.text == "📞 Biz bilan bog'lanish")
async def user_menu_contact(message: Message):
    """Menejer va Instagram bilan bog'lanish"""
    contact_text = (
        "📞 <b>Biz bilan bog'lanish:</b>\n\n"
        f"👨‍💻 <b>Menejer:</b> {config.manager_contact}\n"
        f"📸 <b>Instagram:</b> <a href='{config.instagram_link}'>Instagram sahifamiz</a>\n\n"
        "Savollaringiz bo'lsa bemalol murojaat qilishingiz mumkin!"
    )
    await message.answer(
        text=contact_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=get_main_menu_keyboard()
    )


@user_router.message(F.text == "ℹ️ Biz haqimizda")
async def user_menu_about(message: Message):
    """Biz haqimizda ma'lumot"""
    about_text = (
        f"ℹ️ <b>Biz haqimizda:</b>\n{config.about_me}\n\n"
        f"🤖 <b>Bot imkoniyatlari:</b>\n{config.about_bot}"
    )
    await message.answer(
        text=about_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )


@user_router.message()
async def user_general_fallback(message: Message):
    """Ro'yxatdan o'tgan foydalanuvchi ixtiyoriy matn yozsa"""
    user_id = message.from_user.id if message.from_user else message.chat.id
    user_in_db = await db.get_user(user_id)

    if user_in_db and user_in_db.get("phone_number"):
        await message.answer(
            "Xabaringiz qabul qilindi. Pastdagi tugmalar orqali kerakli bo'limni tanlashingiz yoki menejerimiz bilan bog'lanishingiz mumkin:",
            reply_markup=get_main_menu_keyboard()
        )
