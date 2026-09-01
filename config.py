import os
from typing import Union
from dataclasses import dataclass
from dotenv import load_dotenv

# .env faylini yuklaymiz
load_dotenv()


@dataclass
class Config:
    bot_token: str
    admin_id: int
    channel_id: Union[int, str]
    location_latitude: float
    location_longitude: float
    location_title: str
    location_address: str
    about_me: str
    about_bot: str
    manager_contact: str
    instagram_link: str
    db_path: str = "bot_database.sqlite3"


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    admin_id_str = os.getenv("ADMIN_ID", "0").strip()
    channel_id_raw = os.getenv("CHANNEL_ID", "0").strip()
    manager_contact = os.getenv("MANAGER_CONTACT", "@admin").strip()
    instagram_link = os.getenv("INSTAGRAM_LINK", "https://instagram.com").strip()

    try:
        admin_id = int(admin_id_str)
    except ValueError:
        admin_id = 0

    # Agar @ bilan boshlansa username sifatida olamiz, aks holda int
    if channel_id_raw.startswith("@"):
        channel_id = channel_id_raw
    else:
        try:
            channel_id = int(channel_id_raw)
        except ValueError:
            channel_id = 0

    try:
        lat = float(os.getenv("LOCATION_LATITUDE", "41.311081"))
        lon = float(os.getenv("LOCATION_LONGITUDE", "69.240562"))
    except ValueError:
        lat, lon = 41.311081, 69.240562

    location_title = os.getenv("LOCATION_TITLE", "Bosh Ofis").strip()
    location_address = os.getenv("LOCATION_ADDRESS", "Toshkent sh., Amir Temur ko'chasi, 1-uy").strip()

    about_me = os.getenv(
        "ABOUT_ME",
        "Assalomu alaykum! Bizning sahifamizga xush kelibsiz!"
    ).strip()

    about_bot = os.getenv(
        "ABOUT_BOT",
        "Ushbu bot orqali siz manzilimiz, bino lokatsiyasi va xizmatlarimiz bilan tanishishingiz mumkin."
    ).strip()

    return Config(
        bot_token=bot_token,
        admin_id=admin_id,
        channel_id=channel_id,
        location_latitude=lat,
        location_longitude=lon,
        location_title=location_title,
        location_address=location_address,
        about_me=about_me,
        about_bot=about_bot,
        manager_contact=manager_contact,
        instagram_link=instagram_link,
    )


config = load_config()
