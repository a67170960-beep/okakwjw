"""
Клавиатуры и инлайн-кнопки.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ──────────────────────────────────────────────
#  Главное меню (reply)
# ──────────────────────────────────────────────

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Просмотр юзернеймов"), KeyboardButton(text="🎲 Случайные")],
            [KeyboardButton(text="🔎 Поиск по слову"), KeyboardButton(text="⭐ Избранное")],
            [KeyboardButton(text="📊 Моя статистика"), KeyboardButton(text="ℹ️ О боте")],
        ],
        resize_keyboard=True,
    )


# ──────────────────────────────────────────────
#  Список юзернеймов (50 штук + навигация)
# ──────────────────────────────────────────────

def usernames_kb(
    usernames: list[str],
    current_page: int,
    total_pages: int,
    mode: str = "browse",   # browse | search | random
    query: str = "",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Кнопки с юзернеймами — по 2 в строку
    for i in range(0, len(usernames), 2):
        row = []
        for u in usernames[i:i + 2]:
            row.append(InlineKeyboardButton(
                text=f"@{u}",
                callback_data=f"un:{u}:{current_page}:{mode}:{query[:20]}"
            ))
        builder.row(*row)

    # Навигационная строка
    nav = []
    if current_page > 0:
        nav.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"page:{current_page - 1}:{mode}:{query[:20]}"
        ))
    nav.append(InlineKeyboardButton(
        text=f"📄 {current_page + 1} / {total_pages}",
        callback_data="noop"
    ))
    if current_page < total_pages - 1:
        nav.append(InlineKeyboardButton(
            text="Вперёд ➡️",
            callback_data=f"page:{current_page + 1}:{mode}:{query[:20]}"
        ))
    builder.row(*nav)

    # Быстрый переход
    jump_row = []
    if total_pages > 10:
        jump_row.append(InlineKeyboardButton(
            text="⏮ Первая", callback_data=f"page:0:{mode}:{query[:20]}"
        ))
        jump_row.append(InlineKeyboardButton(
            text="⏭ Последняя", callback_data=f"page:{total_pages - 1}:{mode}:{query[:20]}"
        ))
        builder.row(*jump_row)

    # Обновить (рандом / новая страница)
    extra = []
    if mode == "random":
        extra.append(InlineKeyboardButton(
            text="🔄 Перемешать", callback_data="random:refresh"
        ))
    extra.append(InlineKeyboardButton(
        text="⭐ Мои избранные", callback_data="show_favorites"
    ))
    builder.row(*extra)

    return builder.as_markup()


# ──────────────────────────────────────────────
#  Детальный просмотр юзернейма
# ──────────────────────────────────────────────

def username_detail_kb(
    username: str,
    page: int,
    mode: str,
    query: str,
    is_fav: bool,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    fav_text = "💛 Убрать из избранного" if is_fav else "⭐ В избранное"
    fav_cb = f"unfav:{username}" if is_fav else f"fav:{username}"

    builder.row(InlineKeyboardButton(text="🔗 Открыть в Telegram", url=f"https://t.me/{username}"))
    builder.row(
        InlineKeyboardButton(text=fav_text, callback_data=fav_cb),
        InlineKeyboardButton(text="📋 Скопировать", callback_data=f"copy:{username}"),
    )
    builder.row(InlineKeyboardButton(
        text="◀️ Назад к списку",
        callback_data=f"page:{page}:{mode}:{query[:20]}"
    ))
    return builder.as_markup()


# ──────────────────────────────────────────────
#  Избранное
# ──────────────────────────────────────────────

def favorites_kb(usernames: list[str], page: int = 0, per_page: int = 50) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    total_pages = max(1, (len(usernames) + per_page - 1) // per_page)
    slice_ = usernames[page * per_page:(page + 1) * per_page]

    for i in range(0, len(slice_), 2):
        row = []
        for u in slice_[i:i + 2]:
            row.append(InlineKeyboardButton(
                text=f"@{u}",
                callback_data=f"fav_detail:{u}"
            ))
        builder.row(*row)

    # Навигация
    if total_pages > 1:
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"fav_page:{page - 1}"))
        nav.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton(text="➡️", callback_data=f"fav_page:{page + 1}"))
        builder.row(*nav)

    builder.row(InlineKeyboardButton(text="🗑 Очистить всё", callback_data="fav_clear_confirm"))
    return builder.as_markup()


def fav_detail_kb(username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Открыть в Telegram", url=f"https://t.me/{username}")],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"unfav:{username}"),
            InlineKeyboardButton(text="📋 Скопировать", callback_data=f"copy:{username}"),
        ],
        [InlineKeyboardButton(text="◀️ К избранному", callback_data="show_favorites")],
    ])


def confirm_clear_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, удалить всё", callback_data="fav_clear_yes"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="show_favorites"),
        ]
    ])
