"""
SQLite база данных: избранное и статистика пользователей.
"""

import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bot_data.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, username)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                searches INTEGER DEFAULT 0,
                total_viewed INTEGER DEFAULT 0,
                last_page INTEGER DEFAULT 0,
                last_search TEXT DEFAULT '',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def add_favorite(user_id: int, username: str) -> bool:
    """True если добавлено, False если уже есть."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO favorites (user_id, username) VALUES (?, ?)",
                (user_id, username)
            )
            await db.commit()
        return True
    except aiosqlite.IntegrityError:
        return False


async def remove_favorite(user_id: int, username: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "DELETE FROM favorites WHERE user_id=? AND username=?",
            (user_id, username)
        )
        await db.commit()
        return cur.rowcount > 0


async def get_favorites(user_id: int) -> list[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT username FROM favorites WHERE user_id=? ORDER BY added_at DESC",
            (user_id,)
        )
        rows = await cur.fetchall()
    return [r[0] for r in rows]


async def is_favorite(user_id: int, username: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT 1 FROM favorites WHERE user_id=? AND username=?",
            (user_id, username)
        )
        return await cur.fetchone() is not None


async def update_stats(user_id: int, search: bool = False, viewed: int = 0,
                       page: int | None = None, last_search: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO user_stats (user_id, searches, total_viewed, last_page, last_search)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                searches = searches + ?,
                total_viewed = total_viewed + ?,
                last_page = COALESCE(?, last_page),
                last_search = CASE WHEN ? != '' THEN ? ELSE last_search END
        """, (
            user_id,
            1 if search else 0, viewed,
            page if page is not None else 0, last_search,
            1 if search else 0, viewed,
            page, last_search, last_search,
        ))
        await db.commit()


async def get_user_stats(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT searches, total_viewed, last_page, last_search, joined_at "
            "FROM user_stats WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()
        fav_cur = await db.execute(
            "SELECT COUNT(*) FROM favorites WHERE user_id=?", (user_id,)
        )
        fav_count = (await fav_cur.fetchone())[0]
    if row:
        return {
            "searches": row[0], "total_viewed": row[1],
            "last_page": row[2], "last_search": row[3],
            "joined_at": row[4], "favorites": fav_count,
        }
    return {"searches": 0, "total_viewed": 0, "last_page": 0,
            "last_search": "", "joined_at": "-", "favorites": 0}
