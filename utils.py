from functools import wraps
import bcrypt
from aiogram.types import CallbackQuery, InlineKeyboardMarkup


def edit_message(func):
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        new_text, new_reply_markup = await func(callback, *args, **kwargs)

        if not new_reply_markup:
            new_reply_markup = InlineKeyboardMarkup(inline_keyboard=[])

        await callback.message.edit_text(text=new_text, reply_markup=new_reply_markup)
        await callback.answer()

    return wrapper


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")
