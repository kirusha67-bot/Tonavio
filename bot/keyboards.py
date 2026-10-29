from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.translations import TEXTS


# Временные коллекции для тестирования интерфейса.
# Позже этот список будет автоматически загружаться из базы данных.
TEST_COLLECTIONS = [
    ("Plush Pepe", "plush_pepe"),
    ("Heart Locket", "heart_locket"),
    ("Scared Cat", "scared_cat"),
    ("Durov's Cap", "durovs_cap"),
]


# Главное меню Tonavio
def main_keyboard(language: str):
    t = TEXTS[language]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t["open"],
                    callback_data="open_tonavio"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t["search"],
                    callback_data="search"
                ),
                InlineKeyboardButton(
                    text=t["market"],
                    callback_data="market"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t["scanner"],
                    callback_data="scanner"
                ),
                InlineKeyboardButton(
                    text=t["alerts"],
                    callback_data="alerts"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t["language"],
                    callback_data="language"
                )
            ],
        ]
    )


# Главное меню поиска
def search_keyboard(language: str):
    t = TEXTS[language]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t["search_collection"],
                    callback_data="search_collection"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t["search_model"],
                    callback_data="search_model"
                ),
                InlineKeyboardButton(
                    text=t["search_backdrop"],
                    callback_data="search_backdrop"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t["search_pattern"],
                    callback_data="search_pattern"
                ),
                InlineKeyboardButton(
                    text=t["search_number"],
                    callback_data="search_number"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t["search_price"],
                    callback_data="search_price"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t["search_marketplace"],
                    callback_data="search_marketplace"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t["search_start"],
                    callback_data="search_start"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t["back"],
                    callback_data="back_main"
                )
            ],
        ]
    )


# Выбор коллекции
def collection_keyboard(language: str):
    t = TEXTS[language]

    keyboard = [
        [
            InlineKeyboardButton(
                text=t["all_collections"],
                callback_data="collection_all"
            )
        ]
    ]

    for collection_name, collection_slug in TEST_COLLECTIONS:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"🎁 {collection_name}",
                    callback_data=f"collection_{collection_slug}"
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text=t["back_to_search"],
                callback_data="search"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Выбор языка
def language_keyboard(language: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇬🇧 English",
                    callback_data="lang_en"
                ),
                InlineKeyboardButton(
                    text="🇷🇺 Русский",
                    callback_data="lang_ru"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🇹🇷 Türkçe",
                    callback_data="lang_tr"
                ),
                InlineKeyboardButton(
                    text="🇸🇦 العربية",
                    callback_data="lang_ar"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🇨🇳 中文",
                    callback_data="lang_zh"
                ),
                InlineKeyboardButton(
                    text="🇯🇵 日本語",
                    callback_data="lang_ja"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🇰🇷 한국어",
                    callback_data="lang_ko"
                )
            ],
            [
                InlineKeyboardButton(
                    text=TEXTS[language]["back"],
                    callback_data="back_main"
                )
            ],
        ]
    )