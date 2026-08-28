from aiogram import Bot, F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database as db
from config import ADMIN_IDS
from keyboards import (
    BTN_CANCEL,
    BTN_CHANNEL,
    BTN_COMMENTS,
    BTN_GEMINI,
    BTN_GEMINI_INFO,
    BTN_HELP,
    BTN_INSTRUCTION,
    BTN_REFERRAL,
    admin_order_kb,
    cancel_kb,
    channel_confirm_kb,
    comments_menu_kb,
    help_kb,
    main_menu_kb,
    pay_confirm_kb,
    quantity_kb,
    subscribe_kb,
)
from states import CommentStates, GeminiOrderStates
from utils import fmt_price, split_text

router = Router()


# ---------------------------------------------------------------------------
# Yordamchi funksiyalar
# ---------------------------------------------------------------------------

async def is_subscribed(bot: Bot, channel: str, user_id: int) -> bool:
    if not channel:
        return True
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status not in ("left", "kicked")
    except Exception:
        return False


async def send_main(message_or_cb, is_admin: bool) -> None:
    text = "🏠 Bosh menyu"
    kb = main_menu_kb(is_admin)
    if isinstance(message_or_cb, Message):
        await message_or_cb.answer(text, reply_markup=kb)
    else:
        await message_or_cb.message.answer(text, reply_markup=kb)


async def show_main_menu_or_subscribe(message_or_cb, bot: Bot) -> None:
    user_id = message_or_cb.from_user.id
    if user_id in ADMIN_IDS:
        await send_main(message_or_cb, is_admin=True)
        return
    required_channel = await db.get_setting("required_channel")
    if required_channel and not await is_subscribed(bot, required_channel, user_id):
        text = (
            "❗️ Botdan foydalanish uchun quyidagi kanalga a'zo bo'ling, "
            f"so'ngra \"✅ Tekshirish\" tugmasini bosing:\n\n{required_channel}"
        )
        kb = subscribe_kb(required_channel)
        if isinstance(message_or_cb, Message):
            await message_or_cb.answer(text, reply_markup=kb)
        else:
            await message_or_cb.message.answer(text, reply_markup=kb)
        return
    await send_main(message_or_cb, is_admin=False)


async def ensure_ready(message: Message, bot: Bot) -> bool:
    """Foydalanuvchi kanalga a'zo bo'lmasa, tugmalarga javob bermaydi."""
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        return True
    required_channel = await db.get_setting("required_channel")
    if required_channel and not await is_subscribed(bot, required_channel, user_id):
        text = (
            "❗️ Botdan foydalanish uchun quyidagi kanalga a'zo bo'ling, "
            f"so'ngra \"✅ Tekshirish\" tugmasini bosing:\n\n{required_channel}"
        )
        await message.answer(text, reply_markup=subscribe_kb(required_channel))
        return False
    return True


# ---------------------------------------------------------------------------
# /start va obuna tekshiruvi
# ---------------------------------------------------------------------------

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, command: CommandObject) -> None:
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or ""

    existing = await db.get_user(user_id)
    if not existing:
        referrer_id = None
        if command.args and command.args.startswith("ref_"):
            try:
                candidate_id = int(command.args.replace("ref_", "", 1))
                if candidate_id != user_id and await db.get_user(candidate_id):
                    referrer_id = candidate_id
            except ValueError:
                referrer_id = None

        await db.add_user(user_id, username, full_name, referrer_id)

        if referrer_id:
            new_count = await db.increment_referral(referrer_id)
            if new_count % 10 == 0:
                template = await db.get_setting("referral_template")
                mention = f"@{username}" if username else full_name or f"ID:{user_id}"
                text = template.format(user=mention, count=new_count)
                for admin_id in ADMIN_IDS:
                    try:
                        await bot.send_message(admin_id, text)
                    except Exception:
                        pass

    await show_main_menu_or_subscribe(message, bot)


@router.callback_query(F.data == "check_subscription")
async def cb_check_subscription(callback: CallbackQuery, bot: Bot) -> None:
    required_channel = await db.get_setting("required_channel")
    if await is_subscribed(bot, required_channel, callback.from_user.id):
        try:
            await callback.message.delete()
        except Exception:
            pass
        await send_main(callback, is_admin=callback.from_user.id in ADMIN_IDS)
        await callback.answer("✅ Obuna tasdiqlandi!")
    else:
        await callback.answer("❌ Siz hali kanalga a'zo bo'lmagansiz!", show_alert=True)


# ---------------------------------------------------------------------------
# 💎 Gemini Pro sotib olish
# ---------------------------------------------------------------------------

@router.message(F.text == BTN_GEMINI)
async def gemini_buy_start(message: Message, bot: Bot, state: FSMContext) -> None:
    if not await ensure_ready(message, bot):
        return
    await state.set_state(GeminiOrderStates.choosing_qty)
    await state.update_data(qty=1)
    price = int(await db.get_setting("gemini_price"))
    text = (
        f"💎 Gemini Pro obunasi narxi: {fmt_price(price)} so'm / dona\n\n"
        f"Nechta dona sotib olmoqchisiz?\n\n💰 Jami: {fmt_price(price)} so'm"
    )
    await message.answer(text, reply_markup=quantity_kb(1))


@router.callback_query(GeminiOrderStates.choosing_qty, F.data.in_({"qty_inc", "qty_dec"}))
async def gemini_qty_change(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    qty = data.get("qty", 1)
    if callback.data == "qty_inc" and qty < 10:
        qty += 1
    elif callback.data == "qty_dec" and qty > 1:
        qty -= 1
    await state.update_data(qty=qty)
    price = int(await db.get_setting("gemini_price"))
    total = price * qty
    text = (
        f"💎 Gemini Pro obunasi narxi: {fmt_price(price)} so'm / dona\n\n"
        f"Nechta dona sotib olmoqchisiz?\n\n💰 Jami: {fmt_price(total)} so'm"
    )
    await callback.message.edit_text(text, reply_markup=quantity_kb(qty))
    await callback.answer()


@router.callback_query(GeminiOrderStates.choosing_qty, F.data == "qty_noop")
async def gemini_qty_noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(GeminiOrderStates.choosing_qty, F.data == "qty_cancel")
async def gemini_qty_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer("Bekor qilindi")
    await send_main(callback, is_admin=callback.from_user.id in ADMIN_IDS)


@router.callback_query(GeminiOrderStates.choosing_qty, F.data == "qty_confirm")
async def gemini_qty_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    qty = data.get("qty", 1)
    price = int(await db.get_setting("gemini_price"))
    total = price * qty
    order_id = await db.create_order(callback.from_user.id, "gemini", qty, total)
    await state.clear()

    card_number = await db.get_setting("card_number")
    card_holder = await db.get_setting("card_holder")
    text = (
        "💳 To'lov ma'lumotlari:\n\n"
        f"Karta raqami: {card_number}\n"
        f"Karta egasi: {card_holder}\n"
        f"💰 Summa: {fmt_price(total)} so'm\n\n"
        "To'lovni amalga oshirgach, quyidagi tugmani bosing 👇"
    )
    await callback.message.edit_text(text, reply_markup=pay_confirm_kb(order_id))
    await callback.answer()


# ---------------------------------------------------------------------------
# 🎬 AI Videolar kanali
# ---------------------------------------------------------------------------

@router.message(F.text == BTN_CHANNEL)
async def channel_buy_start(message: Message, bot: Bot) -> None:
    if not await ensure_ready(message, bot):
        return
    price = int(await db.get_setting("channel_price"))
    text = (
        "🎬 AI Videolar yaratishni o'rgatadigan yopiq kanal\n\n"
        f"💰 Narxi: {fmt_price(price)} so'm\n\n"
        "Kanalga a'zo bo'lish uchun to'lovni amalga oshiring."
    )
    await message.answer(text, reply_markup=channel_confirm_kb())


@router.callback_query(F.data == "channel_buy_cancel")
async def channel_buy_cancel(callback: CallbackQuery) -> None:
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer("Bekor qilindi")
    await send_main(callback, is_admin=callback.from_user.id in ADMIN_IDS)


@router.callback_query(F.data == "channel_buy_confirm")
async def channel_buy_confirm(callback: CallbackQuery) -> None:
    price = int(await db.get_setting("channel_price"))
    order_id = await db.create_order(callback.from_user.id, "channel", 1, price)
    card_number = await db.get_setting("card_number")
    card_holder = await db.get_setting("card_holder")
    text = (
        "💳 To'lov ma'lumotlari:\n\n"
        f"Karta raqami: {card_number}\n"
        f"Karta egasi: {card_holder}\n"
        f"💰 Summa: {fmt_price(price)} so'm\n\n"
        "To'lovni amalga oshirgach, quyidagi tugmani bosing 👇"
    )
    await callback.message.edit_text(text, reply_markup=pay_confirm_kb(order_id))
    await callback.answer()


# ---------------------------------------------------------------------------
# Umumiy: buyurtmani bekor qilish / to'lov qildim
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("cancel_order_"))
async def cancel_order(callback: CallbackQuery) -> None:
    order_id = int(callback.data.split("_")[-1])
    await db.update_order_status(order_id, "cancelled")
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer("Bekor qilindi")
    await send_main(callback, is_admin=callback.from_user.id in ADMIN_IDS)


@router.callback_query(F.data.startswith("paid_"))
async def order_paid(callback: CallbackQuery, bot: Bot) -> None:
    order_id = int(callback.data.split("_")[-1])
    order = await db.get_order(order_id)
    if not order or order["status"] != "pending":
        await callback.answer("❌ Buyurtma topilmadi yoki allaqachon yuborilgan", show_alert=True)
        return

    await db.update_order_status(order_id, "awaiting_admin")
    await callback.message.edit_text("⏳ To'lovingiz tekshirilmoqda, iltimos kuting...")
    await callback.answer()

    user = callback.from_user
    product_name = "💎 Gemini Pro" if order["product"] == "gemini" else "🎬 AI Videolar kanali"
    uname = f"@{user.username}" if user.username else user.full_name
    text = (
        "🆕 Yangi to'lov!\n\n"
        f"👤 Foydalanuvchi: {uname} (ID: {user.id})\n"
        f"📦 Mahsulot: {product_name}\n"
        f"🔢 Miqdor: {order['quantity']}\n"
        f"💰 Summa: {fmt_price(order['amount'])} so'm\n"
        f"🆔 Buyurtma: #{order_id}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, reply_markup=admin_order_kb(order_id))
        except Exception:
            pass


# ---------------------------------------------------------------------------
# ℹ️ Gemini nima? / 📖 Yo'riqnoma / 👥 Referal / 🆘 Yordam
# ---------------------------------------------------------------------------

@router.message(F.text == BTN_GEMINI_INFO)
async def gemini_info(message: Message, bot: Bot) -> None:
    if not await ensure_ready(message, bot):
        return
    text = await db.get_setting("gemini_info")
    for chunk in split_text(text):
        await message.answer(chunk)


@router.message(F.text == BTN_INSTRUCTION)
async def instruction(message: Message, bot: Bot) -> None:
    if not await ensure_ready(message, bot):
        return
    text = await db.get_setting("instruction_text")
    for chunk in split_text(text):
        await message.answer(chunk)


@router.message(F.text == BTN_REFERRAL)
async def referral(message: Message, bot: Bot, bot_username: str = "") -> None:
    if not await ensure_ready(message, bot):
        return
    user = await db.get_user(message.from_user.id)
    count = user["referral_count"] if user else 0
    if not bot_username:
        me = await bot.get_me()
        bot_username = me.username
    link = f"https://t.me/{bot_username}?start=ref_{message.from_user.id}"
    text = (
        "👥 Referal dasturi\n\n"
        "Do'stlaringizni taklif qiling va sovg'alarga ega bo'ling!\n\n"
        f"🔗 Sizning havolangiz:\n{link}\n\n"
        f"👤 Taklif qilganlar soni: {count}"
    )
    await message.answer(text)


@router.message(F.text == BTN_HELP)
async def help_handler(message: Message, bot: Bot) -> None:
    if not await ensure_ready(message, bot):
        return
    help_username = await db.get_setting("help_username")
    text = f"🆘 Savol yoki muammolaringiz bo'lsa, admin bilan bog'laning: {help_username}"
    await message.answer(text, reply_markup=help_kb(help_username))


# ---------------------------------------------------------------------------
# 💬 Izohlar
# ---------------------------------------------------------------------------

@router.message(F.text == BTN_COMMENTS)
async def comments_menu(message: Message, bot: Bot) -> None:
    if not await ensure_ready(message, bot):
        return
    await message.answer("💬 Izohlar bo'limi:", reply_markup=comments_menu_kb())


@router.callback_query(F.data == "comment_write")
async def comment_write_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CommentStates.waiting_text)
    await callback.message.answer("✍️ Izohingizni yozing:", reply_markup=cancel_kb())
    await callback.answer()


@router.message(CommentStates.waiting_text, F.text == BTN_CANCEL)
async def comment_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Bekor qilindi", reply_markup=main_menu_kb(message.from_user.id in ADMIN_IDS)
    )


@router.message(CommentStates.waiting_text)
async def comment_save(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("❌ Iltimos, matn ko'rinishida izoh yozing.")
        return
    await db.add_comment(message.from_user.id, message.from_user.username or "", message.text)
    await state.clear()
    await message.answer(
        "✅ Izohingiz uchun rahmat!",
        reply_markup=main_menu_kb(message.from_user.id in ADMIN_IDS),
    )


@router.callback_query(F.data == "comment_view")
async def comment_view(callback: CallbackQuery) -> None:
    comments = await db.get_comments(15)
    if not comments:
        await callback.message.answer("💬 Hozircha izohlar yo'q. Birinchi bo'lib siz yozing!")
        await callback.answer()
        return
    text = "💬 Foydalanuvchilar izohlari:\n\n"
    for c in comments:
        uname = f"@{c['username']}" if c["username"] else "Foydalanuvchi"
        text += f"👤 {uname}:\n{c['text']}\n\n"
    for chunk in split_text(text):
        await callback.message.answer(chunk)
    await callback.answer()
