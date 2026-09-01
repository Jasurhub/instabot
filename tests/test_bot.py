import os
import unittest
import asyncio
from utils import validate_full_name, validate_phone_number
from database import Database


class TestValidation(unittest.TestCase):
    def test_valid_full_names(self):
        valid_cases = [
            ("Jasur Xolboyev", "Jasur Xolboyev"),
            ("ali valiyev", "Ali Valiyev"),
            ("G'ayrat O'tkirov", "G'ayrat O'tkirov"),
            ("Shohruh Mirzo O'rinov", "Shohruh Mirzo O'rinov"),
            ("Джасур Холбоев", "Джасур Холбоев"),
            ("Alisher Navoiy Samarqandiy", "Alisher Navoiy Samarqandiy")
        ]
        for input_name, expected in valid_cases:
            is_valid, res = validate_full_name(input_name)
            self.assertTrue(is_valid, f"Failed for valid name: {input_name} (result: {res})")
            self.assertEqual(res, expected)

    def test_invalid_full_names(self):
        invalid_cases = [
            "",
            "   ",
            "Jasur",  # Faqat ism (1 ta so'z)
            "Jasur123",  # Raqam aralash
            "Jasur Xolboyev 123",  # Raqam
            "https://t.me/jasur",  # Havola
            "@jasur_dev Jasur",  # Belgi / username
            "😊 Jasur Xolboyev",  # Emoji
            "A B C D E F G",  # Haddan tashqari ko'p so'z
            "J X",  # Juda qisqa
        ]
        for input_name in invalid_cases:
            is_valid, res = validate_full_name(input_name)
            self.assertFalse(is_valid, f"Should be invalid: {input_name}")

    def test_valid_phone_numbers(self):
        valid_cases = [
            ("+998901234567", "+998901234567"),
            ("998901234567", "+998901234567"),
            ("901234567", "+998901234567"),
            ("+998 (90) 123-45-67", "+998901234567"),
            ("+12025550123", "+12025550123")
        ]
        for input_phone, expected in valid_cases:
            is_valid, res = validate_phone_number(input_phone)
            self.assertTrue(is_valid, f"Failed for valid phone: {input_phone}")
            self.assertEqual(res, expected)

    def test_invalid_phone_numbers(self):
        invalid_cases = [
            "",
            "salom",
            "12345",
            "+998",
            "99890123456789012345"  # Haddan tashqari uzun
        ]
        for input_phone in invalid_cases:
            is_valid, res = validate_phone_number(input_phone)
            self.assertFalse(is_valid, f"Should be invalid: {input_phone}")


class TestDatabaseAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.test_db_path = "test_bot.sqlite3"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.db = Database(self.test_db_path)
        await self.db.init_db()

    async def asyncTearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    async def test_user_flow(self):
        # 1. /start bosganda
        await self.db.register_start_user(user_id=1001, username="testuser1")
        stats = await self.db.get_users_count()
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["registered"], 0)

        # 2. Ro'yxatdan to'liq o'tganda
        await self.db.add_or_update_user(
            user_id=1001,
            full_name="Jasur Xolboyev",
            phone_number="+998901234567",
            username="testuser1"
        )
        stats = await self.db.get_users_count()
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["registered"], 1)
        self.assertEqual(stats["active"], 1)

        # User ma'lumotlarini olish
        user = await self.db.get_user(1001)
        self.assertIsNotNone(user)
        self.assertEqual(user["full_name"], "Jasur Xolboyev")
        self.assertEqual(user["phone_number"], "+998901234567")

        # Faol ID lar
        active_ids = await self.db.get_all_active_user_ids()
        self.assertIn(1001, active_ids)

        # Bloklash testi
        await self.db.set_user_active(1001, is_active=False)
        active_ids = await self.db.get_all_active_user_ids()
        self.assertNotIn(1001, active_ids)

    async def test_location_settings(self):
        # Dastlabki holatda bo'sh
        loc = await self.db.get_location()
        self.assertIsNone(loc)

        # Admin lokatsiya o'rnatganda
        await self.db.set_location(
            latitude=41.311081,
            longitude=69.240562,
            title="Yangi Ofis",
            address="Toshkent sh., Yunusobod tumani"
        )
        loc = await self.db.get_location()
        self.assertIsNotNone(loc)
        self.assertEqual(loc["latitude"], 41.311081)
        self.assertEqual(loc["longitude"], 69.240562)
        self.assertEqual(loc["title"], "Yangi Ofis")
        self.assertEqual(loc["address"], "Toshkent sh., Yunusobod tumani")

        # Lokatsiyani yangilash
        await self.db.set_location(
            latitude=41.320000,
            longitude=69.250000,
            title="Boshqa Ofis",
            address="Toshkent sh., Chilonzor"
        )
        loc = await self.db.get_location()
        self.assertEqual(loc["latitude"], 41.320000)
        self.assertEqual(loc["title"], "Boshqa Ofis")


if __name__ == "__main__":
    unittest.main()
