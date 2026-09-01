import os
import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramRetryAfter

from config import config
from database import Database
from states import AdminState
from keyboards import get_admin_keyboard, get_cancel_keyboard, get_location_menu_keyboard

logger = logging.getLogger(__name__)
admin_router = Router()
db = Database(config.db_path)


def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish"""
    return user_id == config.admin_id and config.admin_id != 0


def format_stats_text(stats: dict) -> str:
    """Statistika matnini shakllantirish"""
    sources_text = ""
    if "sources" in stats and stats["sources"]:
        sources_text = "\n\n📈 <b>Reklama manbalari (UTM):</b>\n"
        for src, count in stats["sources"].items():
            src_name = src if src != "direct" else "To'g'ridan-to'g'ri (Direct)"
            sources_text += f"▫️ #{src_name}: <b>{count} ta</b>\n"

    return (
        "👑 <b>Admin Boshqaruv Paneli</b>\n\n"
        f"📊 <b>Foydalanuvchilar statistikasi:</b>\n"
        f"▫️ Jami /start bosganlar: <b>{stats['total']} ta</b>\n"
        f"▫️ Ro'yxatdan o'tganlar (telefon qoldirganlar): <b>{stats['registered']} ta</b>\n"
        f"▫️ Faol foydalanuvchilar: <b>{stats['active']} ta</b>"
        f"{sources_text}\n"
        f"Kerakli bo'limni tanlang:"
    )


@admin_router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    """
    /admin komandasi — Admin boshqaruv paneli
    """
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ Kechirasiz, siz ushbu botning administratori emassiz.")
        return

    await state.clear()
    stats = await db.get_users_count()
    admin_text = format_stats_text(stats)

    await message.answer(
        text=admin_text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )


@admin_router.message(F.forward_from_chat)
async def get_forwarded_channel_info(message: Message):
    """Admin biror kanaldan xabarni forward qilib botga yuborganida uning aniq ID sini ko'rsatish"""
    if not is_admin(message.from_user.id):
        return

    chat = message.forward_from_chat
    await message.answer(
        f"📋 <b>Kanal ma'lumotlari aniqlandi:</b>\n\n"
        f"🏷 <b>Kanal nomi:</b> {chat.title}\n"
        f"🆔 <b>Kanal ID si:</b> <code>{chat.id}</code>\n"
        f"📁 <b>Turi:</b> {chat.type}\n\n"
        f"💡 <i>Ushbu ID raqamni nusxalab, <code>.env</code> faylidagi <code>CHANNEL_ID</code> ga yozib qo'yishingiz mumkin.</i>",
        parse_mode="HTML"
    )


@admin_router.callback_query(F.data == "admin_back")
async def cb_admin_back(callback: CallbackQuery, state: FSMContext):
    """Admin bosh menyusiga qaytish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    await state.clear()
    stats = await db.get_users_count()
    admin_text = format_stats_text(stats)

    await callback.message.edit_text(
        text=admin_text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin_location_menu")
async def cb_admin_location_menu(callback: CallbackQuery, state: FSMContext):
    """Lokatsiya boshqaruv menyusi"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    await state.clear()
    await callback.message.edit_text(
        "📍 <b>Bino lokatsiyasini sozlash bo'limi</b>\n\n"
        "Ushbu bo'lim orqali foydalanuvchilarga yuboriladigan ofis/bino lokatsiyasini istalgan vaqt yangilashingiz mumkin.\n\n"
        "Kerakli amalni tanlang:",
        parse_mode="HTML",
        reply_markup=get_location_menu_keyboard()
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin_view_loc")
async def cb_admin_view_loc(callback: CallbackQuery):
    """Joriy lokatsiyani ko'rish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    loc = await db.get_location()
    lat = loc["latitude"] if loc else config.location_latitude
    lon = loc["longitude"] if loc else config.location_longitude
    title = loc["title"] if loc else config.location_title
    address = loc["address"] if loc else config.location_address
    updated_at = loc["updated_at"] if loc else "Boshlang'ich (.env)"

    await callback.message.answer_location(latitude=lat, longitude=lon)
    await callback.message.answer(
        f"📍 <b>Joriy o'rnatilgan lokatsiya:</b>\n\n"
        f"🏢 <b>Bino/Joy:</b> {title}\n"
        f"📌 <b>Manzil:</b> {address}\n"
        f"🌐 <b>Koordinatalar:</b> <code>{lat}, {lon}</code>\n"
        f"🕒 <b>Oxirgi yangilanish:</b> {updated_at}",
        parse_mode="HTML",
        reply_markup=get_location_menu_keyboard()
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin_set_loc")
async def cb_admin_set_loc(callback: CallbackQuery, state: FSMContext):
    """Yangi lokatsiya o'rnatish jarayonini boshlash"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(AdminState.waiting_for_location)
    await callback.message.edit_text(
        "📍 <b>1-QADAM: Yangi geolokatsiyani yuboring</b>\n\n"
        "Telegram orqali yangi binoning joylashuv nuqtasini (Location / Joylashuv) yuboring.\n"
        "<i>(Buning uchun qisqich 📎 belgisini bosib, «Location» bo'limidan xaritadagi nuqtani tanlang)</i>\n\n"
        "Jarayonni bekor qilish uchun pastdagi tugmani bosing:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@admin_router.message(AdminState.waiting_for_location, F.location)
async def process_location_point(message: Message, state: FSMContext):
    """Admin yuborgan lokatsiya koordinatalarini qabul qilish"""
    if not is_admin(message.from_user.id):
        return

    lat = message.location.latitude
    lon = message.location.longitude

    await state.update_data(latitude=lat, longitude=lon)
    await state.set_state(AdminState.waiting_for_location_address)

    await message.answer(
        f"✅ <b>Koordinatalar qabul qilindi:</b> <code>{lat}, {lon}</code>\n\n"
        f"✍️ <b>2-QADAM:</b> Endi ushbu bino nomi va to'liq manzilini yozib yuboring.\n"
        f"<i>(Masalan: Bosh Ofisimiz, Toshkent sh., Chilonzor tumani, 5-mavze)</i>",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@admin_router.message(AdminState.waiting_for_location)
async def process_location_invalid(message: Message):
    """Admin lokatsiya o'rniga boshqa narsa yuborsa"""
    await message.answer(
        "⚠️ Iltimos, Telegram orqali <b>Geolokatsiya (Location)</b> yuboring.\n"
        "📎 Belgisini bosib, «Location» bo'limidan xaritadagi nuqtani tanlang.",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@admin_router.message(AdminState.waiting_for_location_address, F.text)
async def process_location_address(message: Message, state: FSMContext):
    """Bino manzili matnini qabul qilish va bazaga saqlash"""
    if not is_admin(message.from_user.id):
        return

    address_text = message.text.strip()
    data = await state.get_data()
    lat = data.get("latitude")
    lon = data.get("longitude")

    # Manzil va nomini ajratish yoki bitta qilib saqlash
    title = "Ofis / Bino lokatsiyasi"
    address = address_text

    await db.set_location(
        latitude=lat,
        longitude=lon,
        title=title,
        address=address
    )
    await state.clear()

    await message.answer_location(latitude=lat, longitude=lon)
    await message.answer(
        "🎉 <b>Yangi lokatsiya muvaffaqiyatli saqlandi!</b>\n\n"
        f"🏢 <b>Bino/Joy:</b> {title}\n"
        f"📍 <b>Manzil:</b> {address}\n\n"
        f"Endi ro'yxatdan o'tgan barcha mijozlarga aynan ushbu yangilangan lokatsiya yuboriladi.",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )


@admin_router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    """Statistikani yangilab ko'rsatish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    stats = await db.get_users_count()
    admin_text = format_stats_text(stats)

    try:
        await callback.message.edit_text(
            text=admin_text,
            parse_mode="HTML",
            reply_markup=get_admin_keyboard()
        )
    except TelegramBadRequest:
        pass

    await callback.answer("📊 Statistika yangilandi!")


@admin_router.callback_query(F.data == "admin_backup")
async def cb_admin_backup(callback: CallbackQuery, bot: Bot):
    """Bazaning zaxira nusxasini (.sqlite3) adminga yuborish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    if not os.path.exists(config.db_path):
        await callback.answer("⚠️ Ma'lumotlar bazasi fayli topilmadi!", show_alert=True)
        return

    await callback.answer("⏳ Baza fayli yuklanmoqda...")
    try:
        db_file = FSInputFile(config.db_path, filename="bot_database.sqlite3")
        await callback.message.answer_document(
            document=db_file,
            caption="💾 <b>Ma'lumotlar bazasining zaxira nusxasi (Backup)</b>\nUshbu fayl barcha foydalanuvchilar va sozlamalarni o'z ichiga oladi.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Backup yuborishda xatolik: {e}")
        await callback.message.answer(f"❌ Backup yuborishda xatolik yuz berdi: {e}")


@admin_router.callback_query(F.data == "admin_refresh")
async def cb_admin_refresh(callback: CallbackQuery):
    """Panelni yangilash"""
    await cb_admin_stats(callback)


@admin_router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    """Reklama / Xabar yuborish rejimini yoqish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(AdminState.waiting_for_broadcast)
    await callback.message.edit_text(
        "📢 <b>Reklama / Xabar tarqatish bo'limi</b>\n\n"
        "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni jo'nating.\n\n"
        "<i>(Xabar turi istalgancha bo'lishi mumkin: Matn, Rasm, Video, Audio, Forward yoki Tugmali post)</i>\n\n"
        "Jarayonni bekor qilish uchun pastdagi tugmani bosing:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin_cancel")
async def cb_admin_cancel(callback: CallbackQuery, state: FSMContext):
    """Xabar tarqatishni bekor qilish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    await state.clear()
    await callback.message.edit_text(
        "❌ Xabar yuborish bekor qilindi.",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer("Bekor qilindi")


@admin_router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    """To'g'ridan-to'g'ri /broadcast komandasi orqali tarqatish"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ Kechirasiz, siz admin emassiz.")
        return

    await state.set_state(AdminState.waiting_for_broadcast)
    await message.answer(
        "📢 <b>Reklama / Xabar yuborish</b>\n\n"
        "Barcha foydalanuvchilarga tarqatilishi kerak bo'lgan xabarni yuboring:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@admin_router.message(AdminState.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
    """
    Admin yuborgan xabarni barcha faol foydalanuvchilarga tarqatish
    """
    if not is_admin(message.from_user.id):
        return

    user_ids = await db.get_all_active_user_ids()
    total_users = len(user_ids)

    if total_users == 0:
        await message.answer(
            "⚠️ Bazada xabar yuborish uchun faol foydalanuvchilar topilmadi.",
            reply_markup=get_admin_keyboard()
        )
        await state.clear()
        return

    status_msg = await message.answer(
        f"⏳ <b>Xabar tarqatish boshlandi...</b>\n"
        f"Jami foydalanuvchilar: {total_users} ta",
        parse_mode="HTML"
    )

    sent_count = 0
    blocked_count = 0
    failed_count = 0

    for user_id in user_ids:
        try:
            await message.send_copy(chat_id=user_id)
            sent_count += 1
            # Telegram limiti chekloviga tushmaslik uchun kichik kechikish
            await asyncio.sleep(0.05)
        except TelegramForbiddenError:
            # Foydalanuvchi botni bloklagan
            blocked_count += 1
            await db.set_user_active(user_id, is_active=False)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await message.send_copy(chat_id=user_id)
                sent_count += 1
            except Exception:
                failed_count += 1
        except TelegramBadRequest as e:
            failed_count += 1
            logger.warning(f"Bad request for user {user_id}: {e}")
        except Exception as e:
            failed_count += 1
            logger.error(f"Xabar yuborishda xatolik (user_id={user_id}): {e}")

    await state.clear()

    report_text = (
        "✅ <b>Xabar tarqatish yakunlandi!</b>\n\n"
        f"📊 <b>Natijalar:</b>\n"
        f"▫️ Jami qamrov: <b>{total_users} ta</b>\n"
        f"▫️ Muvaffaqiyatli yetkazildi: <b>{sent_count} ta</b>\n"
        f"▫️ Botni bloklaganlar: <b>{blocked_count} ta</b>\n"
        f"▫️ Yetib bormaganlar (xatolik): <b>{failed_count} ta</b>"
    )

    await status_msg.edit_text(
        text=report_text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )
