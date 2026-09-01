import aiosqlite
from typing import List, Optional, Dict, Any
from datetime import datetime


class Database:
    def __init__(self, db_path: str = "bot_database.sqlite3"):
        self.db_path = db_path

    async def init_db(self):
        """Ma'lumotlar bazasi va jadvallarni initsializatsiya qilish"""
        async with aiosqlite.connect(self.db_path) as db:
            # Foydalanuvchilar jadvali
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    full_name TEXT,
                    phone_number TEXT,
                    username TEXT,
                    source TEXT DEFAULT 'direct',
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL
                )
                """
            )
            # Mavjud jadvalda source ustuni bo'lmasa qo'shish (migratsiya)
            try:
                await db.execute("ALTER TABLE users ADD COLUMN source TEXT DEFAULT 'direct'")
            except Exception:
                pass

            # Dinamik lokatsiya va sozlamalar jadvali
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS location_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    title TEXT NOT NULL,
                    address TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            await db.commit()

    async def get_location(self) -> Optional[Dict[str, Any]]:
        """Bazadagi joriy lokatsiyani olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM location_settings WHERE id = 1") as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def set_location(self, latitude: float, longitude: float, title: str, address: str):
        """Admin tomonidan yangi lokatsiyani saqlash"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO location_settings (id, latitude, longitude, title, address, updated_at)
                VALUES (1, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    latitude=excluded.latitude,
                    longitude=excluded.longitude,
                    title=excluded.title,
                    address=excluded.address,
                    updated_at=excluded.updated_at
                """,
                (latitude, longitude, title, address, now)
            )
            await db.commit()

    async def add_or_update_user(
        self,
        user_id: int,
        full_name: str,
        phone_number: str,
        username: Optional[str] = None,
        source: str = "direct"
    ) -> bool:
        """Foydalanuvchi ma'lumotlarini qo'shish yoki yangilash"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO users (user_id, full_name, phone_number, username, source, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, 1, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    full_name=excluded.full_name,
                    phone_number=excluded.phone_number,
                    username=excluded.username,
                    is_active=1
                """,
                (user_id, full_name, phone_number, username, source, now)
            )
            await db.commit()
            return True

    async def register_start_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        source: str = "direct"
    ):
        """Foydalanuvchi /start bosganda dastlabki yozuv yaratish"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO users (user_id, username, source, is_active, created_at)
                VALUES (?, ?, ?, 1, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username=excluded.username,
                    is_active=1
                """,
                (user_id, username, source, now)
            )
            await db.commit()

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Bitta foydalanuvchini ID bo'yicha olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def get_all_active_user_ids(self) -> List[int]:
        """Barcha faol foydalanuvchilar ID ro'yxatini olish (reklama tarqatish uchun)"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT user_id FROM users WHERE is_active = 1") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def get_users_count(self) -> Dict[str, Any]:
        """Foydalanuvchilar statistikasi va manbalar tahlili"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                total = (await cursor.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM users WHERE full_name IS NOT NULL AND phone_number IS NOT NULL") as cursor:
                registered = (await cursor.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM users WHERE is_active = 1") as cursor:
                active = (await cursor.fetchone())[0]

            # Manbalar (UTM) statistikasi
            async with db.execute(
                "SELECT source, COUNT(*) FROM users GROUP BY source ORDER BY COUNT(*) DESC LIMIT 5"
            ) as cursor:
                source_rows = await cursor.fetchall()
                sources = {row[0]: row[1] for row in source_rows}

            return {
                "total": total,
                "registered": registered,
                "active": active,
                "sources": sources
            }

    async def set_user_active(self, user_id: int, is_active: bool):
        """Foydalanuvchi faollik holatini yangilash (botni bloklagan bo'lsa)"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET is_active = ? WHERE user_id = ?",
                (1 if is_active else 0, user_id)
            )
            await db.commit()
