from aiogram.fsm.state import State, StatesGroup


class GeminiOrderStates(StatesGroup):
    choosing_qty = State()


class CommentStates(StatesGroup):
    waiting_text = State()


class AdminStates(StatesGroup):
    waiting_card_number = State()
    waiting_card_holder = State()
    waiting_gemini_price = State()
    waiting_channel_price = State()
    waiting_channel_link = State()
    waiting_help_username = State()
    waiting_required_channel = State()
    waiting_gemini_info = State()
    waiting_instruction = State()
    waiting_referral_template = State()
    waiting_broadcast = State()
    waiting_gemini_link = State()
