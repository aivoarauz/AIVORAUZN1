import asyncio

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database as db
from config import ADMIN_IDS
from keyboards import (
    ABTN_BROADCAST,
    ABTN_CARD_HOLDER,
    ABTN_CARD_NUMBER,
    ABTN_CHANNEL_LINK,
    ABTN_CHANNEL_PRICE,
    ABTN_GEMINI_INFO_EDIT,
    ABTN_GEMINI_PRICE,
    ABTN_HELP_USERNAME,
    ABTN_INSTRUCTION_EDIT,
    ABTN_REFERRAL_TEMPLATE,
    ABTN_REQUIRED_CHANNEL,
    ABTN_STATS,
    ABTN_VIEW_COMMENTS,
    BTN_ADMIN,
    BTN_BACK,
    BTN_CANCEL,
    admin_panel_kb,
    cancel_kb,
    main_menu_kb,
)
from states import AdminStates
from utils import fmt_price, split_text

router = Router()


# ---------------------------------------------------------------------------
# Admin panelga kirish / chiqish
# ---------------------------------------------------------------------------

@router.message(F.text == BTN_ADMIN)
async def open_admin_panel(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("⚙️ Admin panel:", reply_markup=admin_panel_kb())


@router.message(F.text == BTN_BACK)
async def admin_back(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("🏠 Bosh menyu", reply_markup=main_menu_kb(is_admin=True))


# ---------------------------------------------------------------------------
# To'lovlarni tasdiqlash / rad etish
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("approve_"))
async def approve_order(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer()
        return

    order_id = int(callback.data.split("_")[-1])
    order = await db.get_order(order_id)
    if not order or order["status"] != "awaiting_admin":
        await callback.answer("❌ Bu buyurtma allaqachon ko'rib chiqilgan", show_alert=True)
        return

    if order["product"] == "channel":
        channel_link = await db.get_setting("channel_link")
        await db.update_order_status(order_id, "completed")
        try:
            await bot.send_message(
                order["user_id"],
                "✅ To'lovingiz tasdiqlandi!\n\n"
                f"🎬 Yopiq kanal havolasi:\n{channel_link}",
            )
        except Exception:
            pass
        try:
            await callback.message.edit_text(
                callback.message.text + "\n\n✅ Tasdiqlandi va havola yuborildi."
            )
        except Exception:
            pass
    else:
        await db.update_order_status(order_id, "awaiting_link")
        await state.set_state(AdminStates.waiting_gemini_link)
        await state.update_data(order_id=order_id, target_user_id=order["user_id"])
        try:
            await callback.message.edit_text(callback.message.text + "\n\n✅ Tasdiqlandi.")
        except Exception:
            pass
        await callback.message.answer(
            "✏️ Endi foydalanuvchiga yuboriladigan Gemini Pro havolasini yuboring:",
            reply_markup=cancel_kb(),
        )

    await callback.answer()


@router.callback_query(F.data.startswith("reject_"))
async def reject_order(callback: CallbackQuery, bot: Bot) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer()
        return

    order_id = int(callback.data.split("_")[-1])
    order = await db.get_order(order_id)
    if not order or order["status"] != "awaiting_admin":
        await callback.answer("❌ Bu buyurtma allaqachon ko'rib chiqilgan", show_alert=True)
        return

    await db.update_order_status(order_id, "rejected")
    help_username = await db.get_setting("help_username")
    try:
        await bot.send_message(
            order["user_id"],
            "❌ Sizning to'lovingiz rad etildi.\n\n"
            f"Agar xato bo'lgan bo'lsa, admin bilan bog'laning: {help_username}",
        )
    except Exception:
        pass
    try:
        await callback.message.edit_text(callback.message.text + "\n\n❌ Rad etildi.")
    except Exception:
        pass
    await callback.answer()


@router.message(AdminStates.waiting_gemini_link, F.text == BTN_CANCEL)
async def cancel_gemini_link(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Bekor qilindi", reply_markup=admin_panel_kb())


@router.message(AdminStates.waiting_gemini_link)
async def receive_gemini_link(message: Message, bot: Bot, state: FSMContext) -> None:
    data = await state.get_data()
    order_id = data.get("order_id")
    target_user_id = data.get("target_user_id")
    link_text = message.text or ""

    await db.update_order_status(order_id, "completed")
    try:
        await bot.send_message(
            target_user_id,
            "✅ To'lovingiz tasdiqlandi!\n\n"
            f"💎 Sizning Gemini Pro havolangiz:\n{link_text}",
        )
        await message.answer("✅ Havola foydalanuvchiga yuborildi.", reply_markup=admin_panel_kb())
    except Exception:
        await message.answer(
            "❌ Foydalanuvchiga yuborishda xatolik yuz berdi.",
            reply_markup=admin_panel_kb(),
        )
    await state.clear()


# ---------------------------------------------------------------------------
# Sozlamalarni tahrirlash (karta, narxlar, matnlar va h.k.)
# ---------------------------------------------------------------------------

SETTING_HANDLERS = {
    ABTN_CARD_NUMBER: (
        AdminStates.waiting_card_number, "card_number",
        "💳 Yangi karta raqamini kiriting:",
    ),
    ABTN_CARD_HOLDER: (
        AdminStates.waiting_card_holder, "card_holder",
        "👤 Yangi karta egasi F.I.Sh ni kiriting:",
    ),
    ABTN_GEMINI_PRICE: (
        AdminStates.waiting_gemini_price, "gemini_price",
        "💰 Gemini Pro uchun yangi narxni kiriting (faqat raqam, so'm):",
    ),
    ABTN_CHANNEL_PRICE: (
        AdminStates.waiting_channel_price, "channel_price",
        "💰 Kanal uchun yangi narxni kiriting (faqat raqam, so'm):",
    ),
    ABTN_CHANNEL_LINK: (
        AdminStates.waiting_channel_link, "channel_link",
        "🔗 Yangi yopiq kanal havolasini kiriting:",
    ),
    ABTN_HELP_USERNAME: (
        AdminStates.waiting_help_username, "help_username",
        "🆘 Yangi admin nikini kiriting (masalan: @ism):",
    ),
    ABTN_REQUIRED_CHANNEL: (
        AdminStates.waiting_required_channel, "required_channel",
        "📢 Majburiy obuna kanalini kiriting (masalan: @kanal):",
    ),
    ABTN_GEMINI_INFO_EDIT: (
        AdminStates.waiting_gemini_info, "gemini_info",
        "ℹ️ \"Gemini nima?\" tugmasi bosilganda chiqadigan matnni kiriting:",
    ),
    ABTN_INSTRUCTION_EDIT: (
        AdminStates.waiting_instruction, "instruction_text",
        "📖 Yangi yo'riqnoma matnini kiriting:",
    ),
    ABTN_REFERRAL_TEMPLATE: (
        AdminStates.waiting_referral_template, "referral_template",
        "🎉 Yangi referal xabari matnini kiriting.\n\n"
        "Mavjud o'zgaruvchilar: {user} — foydalanuvchi, {count} — odamlar soni",
    ),
}

_ALL_SETTING_STATES = [v[0] for v in SETTING_HANDLERS.values()]


@router.message(F.text.in_(SETTING_HANDLERS.keys()))
async def admin_setting_start(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    target_state, key, prompt = SETTING_HANDLERS[message.text]
    await state.set_state(target_state)
    await state.update_data(setting_key=key)
    await message.answer(prompt, reply_markup=cancel_kb())


@router.message(StateFilter(*_ALL_SETTING_STATES), F.text == BTN_CANCEL)
async def admin_setting_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Bekor qilindi", reply_markup=admin_panel_kb())


@router.message(StateFilter(*_ALL_SETTING_STATES))
async def admin_setting_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    key = data.get("setting_key")
    value = (message.text or "").strip()

    if key in ("gemini_price", "channel_price"):
        if not value.isdigit():
            await message.answer("❌ Faqat raqam kiriting! Qaytadan urinib ko'ring:")
            return

    await db.set_setting(key, value)
    await state.clear()
    await message.answer("✅ Muvaffaqiyatli yangilandi!", reply_markup=admin_panel_kb())


# ---------------------------------------------------------------------------
# 📢 Reklama yuborish (broadcast)
# ---------------------------------------------------------------------------

@router.message(F.text == ABTN_BROADCAST)
async def broadcast_start(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    await state.set_state(AdminStates.waiting_broadcast)
    await message.answer(
        "📢 Barcha foydalanuvchilarga yuboriladigan xabarni yuboring "
        "(matn, rasm, video va h.k.):",
        reply_markup=cancel_kb(),
    )


@router.message(AdminStates.waiting_broadcast, F.text == BTN_CANCEL)
async def broadcast_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Bekor qilindi", reply_markup=admin_panel_kb())


@router.message(AdminStates.waiting_broadcast)
async def broadcast_send(message: Message, bot: Bot, state: FSMContext) -> None:
    await state.clear()
    users = await db.get_all_user_ids()
    sent, failed = 0, 0
    status_msg = await message.answer(f"📤 Yuborilmoqda... 0/{len(users)}")

    for i, uid in enumerate(users, start=1):
        try:
            await bot.copy_message(
                chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id
            )
            sent += 1
        except Exception:
            failed += 1
        if i % 20 == 0:
            await asyncio.sleep(1)

    try:
        await status_msg.edit_text(f"✅ Yuborildi: {sent}\n❌ Xatolik: {failed}")
    except Exception:
        pass
    await message.answer("⚙️ Admin panel:", reply_markup=admin_panel_kb())


# ---------------------------------------------------------------------------
# 📊 Statistika / 💬 Izohlarni ko'rish
# ---------------------------------------------------------------------------

@router.message(F.text == ABTN_STATS)
async def show_stats(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    stats = await db.get_stats()
    text = (
        "📊 Statistika:\n\n"
        f"👥 Foydalanuvchilar: {stats['users']}\n"
        f"💎 Gemini sotilgan: {stats['gemini_sold']}\n"
        f"🎬 Kanal sotilgan: {stats['channel_sold']}\n"
        f"💰 Umumiy tushum: {fmt_price(stats['income'])} so'm"
    )
    await message.answer(text)


@router.message(F.text == ABTN_VIEW_COMMENTS)
async def admin_view_comments(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    comments = await db.get_comments(30)
    if not comments:
        await message.answer("💬 Hozircha izohlar yo'q.")
        return
    text = "💬 So'nggi izohlar:\n\n"
    for c in comments:
        uname = f"@{c['username']}" if c["username"] else f"ID:{c['user_id']}"
        text += f"👤 {uname}:\n{c['text']}\n\n"
    for chunk in split_text(text):
        await message.answer(chunk)
