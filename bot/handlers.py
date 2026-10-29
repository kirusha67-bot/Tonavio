from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from bot.keyboards import (
    main_keyboard,
    language_keyboard,
    search_keyboard,
    collection_keyboard,
)
from bot.translations import TEXTS
from database.db import get_language, set_language


router = Router()


# 🚀 Главное меню
@router.message(CommandStart())
async def start_handler(message: Message):
    language = get_language(message.from_user.id)

    await message.answer(
        TEXTS[language]["welcome"],
        reply_markup=main_keyboard(language),
        parse_mode="HTML",
    )


# 🔎 Поиск подарков
@router.callback_query(F.data == "search")
async def search_handler(callback: CallbackQuery):
    language = get_language(callback.from_user.id)

    text = (
        f'{TEXTS[language]["search_title"]}\n\n'
        f'{TEXTS[language]["search_description"]}'
    )

    await callback.message.edit_text(
        text,
        reply_markup=search_keyboard(language),
        parse_mode="HTML",
    )

    await callback.answer()


# 🎁 Выбор коллекции
@router.callback_query(F.data == "search_collection")
async def search_collection_handler(callback: CallbackQuery):
    language = get_language(callback.from_user.id)

    text = (
        f'{TEXTS[language]["collection_title"]}\n\n'
        f'{TEXTS[language]["collection_description"]}'
    )

    await callback.message.edit_text(
        text,
        reply_markup=collection_keyboard(language),
        parse_mode="HTML",
    )

    await callback.answer()


# 📊 Рынок
@router.callback_query(F.data == "market")
async def market_handler(callback: CallbackQuery):
    language = get_language(callback.from_user.id)

    text = (
        f'{TEXTS[language]["market_title"]}\n\n'
        f'{TEXTS[language]["market_overview"]}'
    )

    await callback.message.edit_text(
        text,
        reply_markup=main_keyboard(language),
        parse_mode="HTML",
    )

    await callback.answer()


# 🌐 Выбор языка
@router.callback_query(F.data == "language")
async def language_handler(callback: CallbackQuery):
    language = get_language(callback.from_user.id)

    await callback.message.edit_text(
        TEXTS[language]["choose_language"],
        reply_markup=language_keyboard(language),
        parse_mode="HTML",
    )

    await callback.answer()


# 🌐 Смена языка
@router.callback_query(F.data.startswith("lang_"))
async def change_language_handler(callback: CallbackQuery):
    language = callback.data.replace("lang_", "")

    if language not in TEXTS:
        await callback.answer("Language error")
        return

    set_language(callback.from_user.id, language)

    await callback.message.edit_text(
        TEXTS[language]["welcome"],
        reply_markup=main_keyboard(language),
        parse_mode="HTML",
    )

    await callback.answer(TEXTS[language]["language_changed"])


# ⬅️ Назад в главное меню
@router.callback_query(F.data == "back_main")
async def back_main_handler(callback: CallbackQuery):
    language = get_language(callback.from_user.id)

    await callback.message.edit_text(
        TEXTS[language]["welcome"],
        reply_markup=main_keyboard(language),
        parse_mode="HTML",
    )

    await callback.answer()