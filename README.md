# 🤖 Instagram Telegram Lead & Lokatsiya Boti

Ushbu Telegram bot Instagram profilingizdan (bio yoki reklama havolasidan) kirgan mijozlar (leadlar) ma'lumotlarini qabul qilish, bino lokatsiyasini yuborish, ma'lumotlarni Telegram kanalingizga chiroyli tartibda jo'natish va adminga barcha foydalanuvchilarga reklama/xabar tarqatish uchun mo'ljallangan.

---

## 🌟 Asosiy Imkoniyatlar

1. **Foydalanuvchi Oqimi**:
   - `/start` bosilganda: Siz va bot haqida ma'lumot beriladi.
   - **Ism va Familiya filtri**: Faqat haqiqiy ism va familiya (kamida 2 ta so'z, faqat harflar, raqam va begona belgilarsiz) qabul qilinadi.
   - **Telefon raqami**: "📱 Telefon raqamni yuborish" tugmasi orqali yoki qo'lda kiritish varianti.
   - **Lokatsiya**: Foydalanuvchi ro'yxatdan o'tgach, ofis/bino geolokatsiyasi (xarita nuqtasi) va to'liq manzil matni yuboriladi.

2. **Kanalga Hisobot Yuborish**:
   - Har bir yangi foydalanuvchi ro'yxatdan o'tganida uning barcha ma'lumotlari (Ismi, Telefoni, Username, Telegram ID, Vaqti) belgilangan Telegram kanalga tartibli va chiroyli dizaynda yuboriladi.

3. **Admin Boshqaruv Paneli (`/admin`)**:
   - 📊 **Statistika**: Jami start bosganlar, ro'yxatdan o'tganlar va faol foydalanuvchilar soni.
   - 📢 **Xabar yuborish (Broadcast)**: Barcha start bosgan foydalanuvchilarga reklama, matn, rasm, video, audio yoki postlarni bir martada tarqatish.
   - 🛡 Botni bloklagan foydalanuvchilarni xatosiz aniqlash va hisobot berish.

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Talablar
- Python 3.10 yoki undan yuqori versiya.

### 2. Kutubxonalarni o'rnatish
Virtual muhitni faollashtiring va paketlarni o'rnating:
```bash
pip install -r requirements.txt
```

### 3. `.env` Faylini Sozlash
Loyiha papkasidagi `.env` faylini oching va o'z ma'lumotlaringizni kiriting:

```env
# 1. @BotFather dan olingan bot tokeni
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ

# 2. Sizning Telegram ID raqamingiz (@userinfobot orqali bilsa bo'ladi)
ADMIN_ID=123456789

# 3. Ro'yxatdan o'tganlar tushadigan Telegram kanal ID si (Bot kanalga admin bo'lishi shart)
CHANNEL_ID=-1001234567890

# 4. Bino lokatsiyasi koordinatalari (Google Maps yoki Yandex Maps dan)
LOCATION_LATITUDE=41.311081
LOCATION_LONGITUDE=69.240562

# 5. Bino nomi va manzili
LOCATION_TITLE=Bosh Ofisimiz
LOCATION_ADDRESS=Toshkent sh., Amir Temur ko'chasi, 1-uy

# 6. Start bosganda ko'rinadigan ma'lumotlar
ABOUT_ME=Assalomu alaykum! Bizning kompaniyamizga xush kelibsiz!
ABOUT_BOT=Ushbu bot orqali siz manzilimiz, xizmatlarimiz va takliflarimiz bilan tanishishingiz mumkin.
```

---

## 📌 Muhim Ma'lumotlarni Qanday Olish Mumkin?

### 1. `BOT_TOKEN` olish:
- Telegramda [@BotFather](https://t.me/BotFather) botiga kiring.
- `/newbot` buyrug'ini yuboring va ko'rsatmalarga asosan botingizga nom va username bering.
- Berilgan API Tokenni nusxalab oling.

### 2. `ADMIN_ID` olish:
- Telegramda [@userinfobot](https://t.me/userinfobot) botiga `/start` yuboring.
- `Id:` qatoridagi raqamni nusxalab oling.

### 3. `CHANNEL_ID` olish va kanalni ulash:
1. Telegramda yangi kanal yoki guruh oching.
2. Botingizni kanalingizga **Admin (Administrator)** qilib qo'shing (xabar yozish ruxsati bilan).
3. Kanal ID sini bilish uchun:
   - [@username_to_id_bot](https://t.me/username_to_id_bot) yoki [@JsonDumpBot](https://t.me/JsonDumpBot) ga kanaldan birorta xabarni Forward (uzatish) qiling.
   - Chiqqan ID raqamni (masalan: `-1002345678901`) `.env` dagi `CHANNEL_ID` ga yozing.
   *(Eslatma: Agar kanalga yuborish kerak bo'lmasa, `CHANNEL_ID=0` qoldirishingiz mumkin).*

### 4. Koordinatalarni olish:
- [Google Maps](https://maps.google.com) yoki Yandex xaritasidan kerakli manzil ustiga bosing — kenglik va uzunlik raqamlari chiqadi (masalan, `41.311081, 69.240562`).

---

## ▶️ Botni Ishga Tushirish

```bash
python main.py
```

yoki virtual muhit orqali:
```bash
.venv/bin/python main.py
```

---

## 👑 Admin Imkoniyatlaridan Foydalanish

Telegramda botingizga kirib `/admin` deb yozing:

1. **📊 Statistika**:
   - Jami `/start` bosganlar va to'liq telefon qoldirganlar sonini real vaqtda ko'rasiz.

2. **📍 Lokatsiyani sozlash (Joy o'zgarganda yangilash)**:
   - «📍 Lokatsiyani sozlash» tugmasini bosing.
   - **👀 Joriy lokatsiyani ko'rish**: Hozirda qaysi joy o'rnatilganini xarita va manzil bilan ko'rsatadi.
   - **✏️ Yangi lokatsiya o'rnatish**:
     1. Telegram orqali yangi binoning **Location (Joylashuv)** nuqtasini yuborasiz (📎 -> Location).
     2. Bino nomi va yangi manzil matnini yozasiz.
     3. Bot yangilangan lokatsiyani saqlaydi va bundan keyin barcha yangi ro'yxatdan o'tganlarga aynan shu yangi lokatsiyani yuboradi!

3. **📢 Xabar yuborish (Reklama / Broadcast)**:
   - Istalgan xabar (matn, rasm, video, havola, post) yuborsangiz, bot uni barcha foydalanuvchilarga tarqatadi va nechta odamga yetib borgani bo'yicha hisobot beradi.
