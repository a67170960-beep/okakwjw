"""
Все хендлеры бота.
"""

import asyncio
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import (
    main_menu_kb, usernames_kb, username_detail_kb,
    favorites_kb, fav_detail_kb, confirm_clear_kb,
)
from usernames import get_page, search_usernames, get_random_usernames, get_total_count, get_stats
from database import (
    add_favorite, remove_favorite, get_favorites,
    is_favorite, update_stats, get_user_stats,
)

router = Router()

PER_PAGE = 50


# ════════════════════════════════════════════
#  FSM
# ════════════════════════════════════════════

class SearchState(StatesGroup):
    waiting_query = State()


# ════════════════════════════════════════════
#  START / HELP
# ════════════════════════════════════════════

@router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    total = get_total_count()
    text = (
        f"👋 <b>Привет, {msg.from_user.first_name}!</b>\n\n"
        f"🔍 Я помогу найти свободный юзернейм для Telegram.\n"
        f"📦 В базе <b>{total:,}</b> вариантов!\n\n"
        "Выбери действие в меню ниже 👇"
    )
    await msg.answer(text, parse_mode="HTML", reply_markup=main_menu_kb())


@router.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        "📖 <b>Команды:</b>\n\n"
        "/start — главное меню\n"
        "/browse — просмотр юзернеймов\n"
        "/random — случайные юзернеймы\n"
        "/search — поиск по слову\n"
        "/favorites — избранное\n"
        "/stats — статистика\n"
        "/info — о боте\n\n"
        "<b>Как пользоваться:</b>\n"
        "• Листай страницы по 50 штук\n"
        "• Тапни на @юзернейм для деталей\n"
        "• Добавляй в ⭐ избранное\n"
        "• Ищи нужные слова через 🔎",
        parse_mode="HTML",
    )


# ════════════════════════════════════════════
#  BROWSE (обзор по страницам)
# ════════════════════════════════════════════

async def send_browse_page(target, page: int, mode: str = "browse", query: str = ""):
    if mode == "search" and query:
        usernames, total_pages = search_usernames(query, page, PER_PAGE)
        header = f"🔎 <b>Поиск:</b> «{query}»\nНайдено страниц: {total_pages}"
    else:
        usernames, total_pages = get_page(page, PER_PAGE)
        header = f"📋 <b>Список юзернеймов</b>\nСтраница {page + 1} из {total_pages}"

    if not usernames:
        text = "😔 Ничего не найдено по вашему запросу."
        if hasattr(target, "message"):
            await target.message.edit_text(text)
        else:
            await target.answer(text, reply_markup=main_menu_kb())
        return

    text = (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📄 Показано: <b>{len(usernames)}</b> из {total_pages * PER_PAGE:,}+\n"
        f"👆 Нажми на @username для деталей"
    )
    kb = usernames_kb(usernames, page, total_pages, mode, query)

    if isinstance(target, CallbackQuery):
        try:
            await target.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            await target.answer()
    else:
        await target.answer(text, parse_mode="HTML", reply_markup=kb)


@router.message(F.text == "🔍 Просмотр юзернеймов")
@router.message(Command("browse"))
async def cmd_browse(msg: Message, state: FSMContext):
    await state.clear()
    await update_stats(msg.from_user.id, viewed=PER_PAGE, page=0)
    await send_browse_page(msg, 0, "browse")


# ════════════════════════════════════════════
#  RANDOM
# ════════════════════════════════════════════

async def send_random(target):
    usernames = get_random_usernames(PER_PAGE)
    total = get_total_count()
    text = (
        f"🎲 <b>Случайные юзернеймы</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Всего в базе: <b>{total:,}</b>\n"
        f"🔄 Каждый раз новая подборка!"
    )
    kb = usernames_kb(usernames, 0, 1, "random", "")

    if isinstance(target, CallbackQuery):
        try:
            await target.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            await target.answer("Обновлено!")
    else:
        await target.answer(text, parse_mode="HTML", reply_markup=kb)


@router.message(F.text == "🎲 Случайные")
@router.message(Command("random"))
async def cmd_random(msg: Message):
    await update_stats(msg.from_user.id, viewed=PER_PAGE)
    await send_random(msg)


@router.callback_query(F.data == "random:refresh")
async def cb_random_refresh(cb: CallbackQuery):
    await update_stats(cb.from_user.id, viewed=PER_PAGE)
    await send_random(cb)


# ════════════════════════════════════════════
#  ПОИСК
# ════════════════════════════════════════════

@router.message(F.text == "🔎 Поиск по слову")
@router.message(Command("search"))
async def cmd_search_start(msg: Message, state: FSMContext):
    await state.set_state(SearchState.waiting_query)
    await msg.answer(
        "🔎 <b>Поиск юзернеймов</b>\n\n"
        "Введи слово или часть слова:\n"
        "<i>Например: wolf, dark, pro, 777...</i>",
        parse_mode="HTML",
    )


@router.message(SearchState.waiting_query)
async def process_search(msg: Message, state: FSMContext):
    query = msg.text.strip().lower()
    if len(query) < 2:
        await msg.answer("⚠️ Минимум 2 символа для поиска.")
        return
    await state.clear()
    await update_stats(msg.from_user.id, search=True, last_search=query, viewed=PER_PAGE)
    await send_browse_page(msg, 0, "search", query)


# ════════════════════════════════════════════
#  ПАГИНАЦИЯ (callback)
# ════════════════════════════════════════════

@router.callback_query(F.data.startswith("page:"))
async def cb_page(cb: CallbackQuery):
    parts = cb.data.split(":")
    page = int(parts[1])
    mode = parts[2] if len(parts) > 2 else "browse"
    query = parts[3] if len(parts) > 3 else ""
    await update_stats(cb.from_user.id, viewed=PER_PAGE, page=page)
    await send_browse_page(cb, page, mode, query)


# ════════════════════════════════════════════
#  ДЕТАЛЬНЫЙ ПРОСМОТР ЮЗЕРНЕЙМА
# ════════════════════════════════════════════

@router.callback_query(F.data.startswith("un:"))
async def cb_username_detail(cb: CallbackQuery):
    parts = cb.data.split(":")
    username = parts[1]
    page = int(parts[2])
    mode = parts[3] if len(parts) > 3 else "browse"
    query = parts[4] if len(parts) > 4 else ""

    fav = await is_favorite(cb.from_user.id, username)

    # Анализ юзернейма
    has_num = any(c.isdigit() for c in username)
    has_under = "_" in username
    length = len(username)

    # Оценка "крутости"
    score = 10
    if length <= 8:
        score += 3
    if length <= 6:
        score += 2
    if not has_num:
        score += 2
    if not has_under:
        score += 1

    stars = "⭐" * min(score // 3, 5)

    text = (
        f"🔍 <b>@{username}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📏 Длина: <b>{length}</b> симв.\n"
        f"🔢 Цифры: {'есть' if has_num else 'нет'}\n"
        f"〰️ Подчёркивание: {'есть' if has_under else 'нет'}\n"
        f"✨ Рейтинг: {stars}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ Статус: <i>возможно свободен</i>\n"
        f"🔗 <code>https://t.me/{username}</code>"
    )

    kb = username_detail_kb(username, page, mode, query, fav)
    try:
        await cb.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await cb.answer()


# ════════════════════════════════════════════
#  КОПИРОВАНИЕ
# ════════════════════════════════════════════

@router.callback_query(F.data.startswith("copy:"))
async def cb_copy(cb: CallbackQuery):
    username = cb.data.split(":")[1]
    await cb.answer(f"@{username} — скопируй из текста выше!", show_alert=True)


# ════════════════════════════════════════════
#  ИЗБРАННОЕ
# ════════════════════════════════════════════

@router.message(F.text == "⭐ Избранное")
@router.message(Command("favorites"))
@router.callback_query(F.data == "show_favorites")
async def cmd_favorites(event):
    if isinstance(event, CallbackQuery):
        user_id = event.from_user.id
    else:
        user_id = event.from_user.id

    favs = await get_favorites(user_id)
    if not favs:
        text = "⭐ <b>Избранное пусто</b>\n\nДобавляй юзернеймы нажав на кнопку ⭐ при просмотре!"
        if isinstance(event, CallbackQuery):
            try:
                await event.message.edit_text(text, parse_mode="HTML")
            except Exception:
                await event.answer(text)
        else:
            await event.answer(text, parse_mode="HTML")
        return

    text = f"⭐ <b>Избранное</b> — {len(favs)} юзернеймов\nТапни, чтобы открыть детали:"
    kb = favorites_kb(favs)

    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            await event.answer()
    else:
        await event.answer(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data.startswith("fav_page:"))
async def cb_fav_page(cb: CallbackQuery):
    page = int(cb.data.split(":")[1])
    favs = await get_favorites(cb.from_user.id)
    text = f"⭐ <b>Избранное</b> — {len(favs)} юзернеймов:"
    kb = favorites_kb(favs, page)
    try:
        await cb.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await cb.answer()


@router.callback_query(F.data.startswith("fav_detail:"))
async def cb_fav_detail(cb: CallbackQuery):
    username = cb.data.split(":")[1]
    text = (
        f"⭐ <b>Избранное: @{username}</b>\n\n"
        f"🔗 <code>https://t.me/{username}</code>"
    )
    await cb.message.edit_text(text, parse_mode="HTML", reply_markup=fav_detail_kb(username))


@router.callback_query(F.data.startswith("fav:"))
async def cb_add_fav(cb: CallbackQuery):
    username = cb.data.split(":")[1]
    added = await add_favorite(cb.from_user.id, username)
    if added:
        await cb.answer(f"⭐ @{username} добавлен в избранное!", show_alert=False)
    else:
        await cb.answer("Уже в избранном!", show_alert=False)
    # Обновим кнопки
    fav = True
    parts = cb.message.reply_markup.inline_keyboard
    # Редактируем текущее сообщение
    try:
        text = cb.message.text
        # Парсим из callback_data страницу и режим
        # Ищем кнопку "Назад к списку" чтобы достать page/mode/query
        back_cb = None
        for row in parts:
            for btn in row:
                if btn.callback_data and btn.callback_data.startswith("page:"):
                    back_cb = btn.callback_data
        if back_cb:
            p = back_cb.split(":")
            page = int(p[1])
            mode = p[2] if len(p) > 2 else "browse"
            query = p[3] if len(p) > 3 else ""
            await cb.message.edit_reply_markup(
                reply_markup=username_detail_kb(username, page, mode, query, True)
            )
    except Exception:
        pass


@router.callback_query(F.data.startswith("unfav:"))
async def cb_remove_fav(cb: CallbackQuery):
    username = cb.data.split(":")[1]
    removed = await remove_favorite(cb.from_user.id, username)
    if removed:
        await cb.answer(f"🗑 @{username} удалён из избранного", show_alert=False)
    else:
        await cb.answer("Не найдено в избранном.", show_alert=False)

    # Если мы в детальном виде избранного — вернём к списку
    try:
        text = cb.message.text
        if "Избранное:" in text:
            await cmd_favorites(cb)
            return
        # Иначе обновим кнопки детального просмотра
        parts = cb.message.reply_markup.inline_keyboard
        back_cb = None
        for row in parts:
            for btn in row:
                if btn.callback_data and btn.callback_data.startswith("page:"):
                    back_cb = btn.callback_data
        if back_cb:
            p = back_cb.split(":")
            page = int(p[1])
            mode = p[2] if len(p) > 2 else "browse"
            query = p[3] if len(p) > 3 else ""
            await cb.message.edit_reply_markup(
                reply_markup=username_detail_kb(username, page, mode, query, False)
            )
    except Exception:
        pass


@router.callback_query(F.data == "fav_clear_confirm")
async def cb_fav_clear_confirm(cb: CallbackQuery):
    await cb.message.edit_text(
        "⚠️ <b>Подтверди удаление</b>\n\nУдалить ВСЕ избранные юзернеймы?",
        parse_mode="HTML",
        reply_markup=confirm_clear_kb(),
    )


@router.callback_query(F.data == "fav_clear_yes")
async def cb_fav_clear(cb: CallbackQuery):
    from database import DB_PATH
    import aiosqlite
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM favorites WHERE user_id=?", (cb.from_user.id,))
        await db.commit()
    await cb.answer("✅ Избранное очищено!", show_alert=False)
    await cb.message.edit_text("⭐ Избранное очищено.")


# ════════════════════════════════════════════
#  СТАТИСТИКА
# ════════════════════════════════════════════

@router.message(F.text == "📊 Моя статистика")
@router.message(Command("stats"))
async def cmd_stats(msg: Message):
    us = await get_user_stats(msg.from_user.id)
    gs = get_stats()
    text = (
        f"📊 <b>Твоя статистика</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔍 Поисков: <b>{us['searches']}</b>\n"
        f"👁 Просмотрено: <b>{us['total_viewed']:,}</b>\n"
        f"⭐ Избранных: <b>{us['favorites']}</b>\n"
        f"📄 Последняя страница: <b>{us['last_page'] + 1}</b>\n"
        f"🔎 Последний поиск: <b>{us['last_search'] or '—'}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>База юзернеймов</b>\n"
        f"Всего: <b>{gs['total']:,}</b>\n"
        f"Средняя длина: <b>{gs['avg_len']}</b> симв.\n"
        f"С цифрами: <b>{gs['with_numbers']:,}</b>\n"
        f"С подчёркиванием: <b>{gs['with_underscore']:,}</b>"
    )
    await msg.answer(text, parse_mode="HTML", reply_markup=main_menu_kb())


# ════════════════════════════════════════════
#  О БОТЕ
# ════════════════════════════════════════════

@router.message(F.text == "ℹ️ О боте")
@router.message(Command("info"))
async def cmd_info(msg: Message):
    total = get_total_count()
    text = (
        f"ℹ️ <b>Username Finder Bot</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔍 Помогает найти свободный красивый юзернейм для Telegram.\n\n"
        f"📦 <b>{total:,}</b> вариантов в базе\n"
        f"📄 Листай по 50 штук\n"
        f"⭐ Сохраняй понравившиеся\n"
        f"🔎 Ищи по ключевым словам\n"
        f"🎲 Получай случайные подборки\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ <b>Важно:</b> бот показывает <i>потенциально</i> свободные "
        f"юзернеймы. Перед регистрацией проверь наличие по ссылке t.me/username.\n\n"
        f"✅ Требования Telegram: 5–32 символа, a-z, 0-9, _"
    )
    await msg.answer(text, parse_mode="HTML", reply_markup=main_menu_kb())


# ════════════════════════════════════════════
#  NOOP (заглушка для кнопок-счётчиков)
# ════════════════════════════════════════════

@router.callback_query(F.data == "noop")
async def cb_noop(cb: CallbackQuery):
    await cb.answer()
