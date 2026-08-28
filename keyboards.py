from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# ---------------------------------------------------------------------------
# Matn konstantalari (asosiy menyu)
# ---------------------------------------------------------------------------

BTN_GEMINI = "💎 Gemini Pro sotib olish"
BTN_CHANNEL = "🎬 AI Videolar kanali"
BTN_GEMINI_INFO = "ℹ️ Gemini nima?"
BTN_INSTRUCTION = "📖 Yo'riqnoma"
BTN_REFERRAL = "👥 Referal dasturi"
BTN_COMMENTS = "💬 Izohlar"
BTN_HELP = "🆘 Yordam"
BTN_ADMIN = "⚙️ Admin panel"

BTN_CANCEL = "❌ Bekor qilish"
BTN_BACK = "⬅️ Orqaga"

# ---------------------------------------------------------------------------
# Matn konstantalari (admin panel)
# ---------------------------------------------------------------------------

ABTN_CARD_NUMBER = "💳 Karta raqami"
ABTN_CARD_HOLDER = "👤 Karta egasi"
ABTN_GEMINI_PRICE = "💰 Gemini narxi"
ABTN_CHANNEL_PRICE = "💰 Kanal narxi"
ABTN_CHANNEL_LINK = "🔗 Kanal linki"
ABTN_HELP_USERNAME = "🆘 Yordam nik"
ABTN_REQUIRED_CHANNEL = "📢 Majburiy kanal"
ABTN_GEMINI_INFO_EDIT = "ℹ️ Gemini ma'lumoti"
ABTN_INSTRUCTION_EDIT = "📖 Yo'riqnoma matni"
ABTN_REFERRAL_TEMPLATE = "🎉 Referal xabari"
ABTN_BROADCAST = "📢 Reklama yuborish"
ABTN_STATS = "📊 Statistika"
ABTN_VIEW_COMMENTS = "💬 Izohlarni ko'rish"


# ---------------------------------------------------------------------------
# Reply keyboards (pastda doimiy chiqib turadigan tugmalar)
# ---------------------------------------------------------------------------

def main_menu_kb(is_admin: bool = False) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN_GEMINI)
    kb.button(text=BTN_CHANNEL)
    kb.button(text=BTN_GEMINI_INFO)
    kb.button(text=BTN_INSTRUCTION)
    kb.button(text=BTN_REFERRAL)
    kb.button(text=BTN_COMMENTS)
    kb.button(text=BTN_HELP)
    if is_admin:
        kb.button(text=BTN_ADMIN)
        kb.adjust(2, 2, 2, 1, 1)
    else:
        kb.adjust(2, 2, 2, 1)
    return kb.as_markup(resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN_CANCEL)
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def admin_panel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for text in (
        ABTN_CARD_NUMBER, ABTN_CARD_HOLDER, ABTN_GEMINI_PRICE, ABTN_CHANNEL_PRICE,
        ABTN_CHANNEL_LINK, ABTN_HELP_USERNAME, ABTN_REQUIRED_CHANNEL,
        ABTN_GEMINI_INFO_EDIT, ABTN_INSTRUCTION_EDIT, ABTN_REFERRAL_TEMPLATE,
        ABTN_BROADCAST, ABTN_STATS, ABTN_VIEW_COMMENTS, BTN_BACK,
    ):
        kb.button(text=text)
    kb.adjust(2, 2, 2, 2, 2, 2, 2)
    return kb.as_markup(resize_keyboard=True)


# ---------------------------------------------------------------------------
# Inline keyboards
# ---------------------------------------------------------------------------

def subscribe_kb(channel_username: str) -> InlineKeyboardMarkup:
    channel_link = f"https://t.me/{channel_username.lstrip('@')}"
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Kanalga o'tish", url=channel_link)
    kb.button(text="✅ Tekshirish", callback_data="check_subscription")
    kb.adjust(1)
    return kb.as_markup()


def quantity_kb(qty: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➖", callback_data="qty_dec")
    kb.button(text=f"{qty} ta", callback_data="qty_noop")
    kb.button(text="➕", callback_data="qty_inc")
    kb.button(text="✅ Sotib olish", callback_data="qty_confirm")
    kb.button(text=BTN_CANCEL, callback_data="qty_cancel")
    kb.adjust(3, 1, 1)
    return kb.as_markup()


def pay_confirm_kb(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ To'lov qildim", callback_data=f"paid_{order_id}")
    kb.button(text=BTN_CANCEL, callback_data=f"cancel_order_{order_id}")
    kb.adjust(1)
    return kb.as_markup()


def channel_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Sotib olish", callback_data="channel_buy_confirm")
    kb.button(text=BTN_CANCEL, callback_data="channel_buy_cancel")
    kb.adjust(1)
    return kb.as_markup()


def admin_order_kb(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Tasdiqlash", callback_data=f"approve_{order_id}")
    kb.button(text="❌ Rad etish", callback_data=f"reject_{order_id}")
    kb.adjust(2)
    return kb.as_markup()


def comments_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✍️ Izoh yozish", callback_data="comment_write")
    kb.button(text="📋 Izohlarni ko'rish", callback_data="comment_view")
    kb.adjust(1)
    return kb.as_markup()


def help_kb(help_username: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="✉️ Admin bilan bog'lanish",
        url=f"https://t.me/{help_username.lstrip('@')}",
    )
    kb.adjust(1)
    return kb.as_markup()
