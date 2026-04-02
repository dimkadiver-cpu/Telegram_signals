from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def draft_keyboard(draft_id: int) -> InlineKeyboardMarkup:
    """Inline keyboard attached to every review draft."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Approva", callback_data=f"approve:{draft_id}"),
        InlineKeyboardButton(text="✏️ Modifica", callback_data=f"edit:{draft_id}"),
        InlineKeyboardButton(text="🗑 Elimina", callback_data=f"delete:{draft_id}"),
    ]])
