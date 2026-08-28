# 🤖 Telegram Savdo Boti (Gemini Pro + AI Videolar kanali)

Bu bot orqali siz:
- 💎 **Gemini Pro** obunasini sotasiz (1 tadan 10 tagacha, narxi admin panelda o'zgartiriladi)
- 🎬 **AI Videolar** bo'yicha yopiq kanal linkini sotasiz
- 💳 To'lovni karta orqali qabul qilib, admin tasdiqlagandan keyin mahsulotni avtomatik yuborasiz
- 👥 Referal dasturi orqali foydalanuvchilarni jalb qilasiz
- 💬 Foydalanuvchilar izoh qoldira oladi
- ⚙️ Hamma narsani (narx, karta, matnlar, linklar) botning o'zidan, admin panel orqali o'zgartira olasiz

---

## 📁 Fayllar tuzilishi

```
telegram_shop_bot/
├── bot.py                 # Botni ishga tushiruvchi asosiy fayl
├── config.py               # Sozlamalar (.env dan o'qiydi)
├── database.py              # SQLite ma'lumotlar bazasi funksiyalari
├── keyboards.py             # Barcha tugmalar (reply va inline)
├── states.py                # FSM holatlari (ketma-ket savol-javoblar uchun)
├── utils.py                 # Yordamchi funksiyalar
├── handlers/
│   ├── user.py               # Oddiy foydalanuvchi funksiyalari
│   └── admin.py               # Admin panel funksiyalari
├── requirements.txt          # Kerakli kutubxonalar
├── render.yaml                # Render.com uchun sozlama fayli (ixtiyoriy)
├── .env.example                # Namuna environment fayli
└── README.md                   # Ushbu fayl
```

---

## 1️⃣ Bot yaratish va sozlash

1. Telegramda **@BotFather** ga yozing, `/newbot` buyrug'ini yuboring va botga nom bering.
   BotFather sizga **BOT_TOKEN** beradi — uni saqlab qo'ying.
2. O'zingizning Telegram ID raqamingizni bilish uchun **@userinfobot** ga yozing.
   U sizga ID raqamingizni beradi (masalan: `123456789`) — bu **ADMIN_IDS** bo'ladi.
3. Botni sizning **@aivora_uz** kanalingizga hamda sotiladigan yopiq kanalga
   **admin** qilib qo'shing (kamida "a'zolarni ko'rish" huquqi bilan) —
   aks holda bot foydalanuvchining obunasini tekshira olmaydi.

---

## 2️⃣ Lokal kompyuterda ishga tushirish (sinov uchun)

```bash
cd telegram_shop_bot
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# .env faylini oching va BOT_TOKEN, ADMIN_IDS qiymatlarini kiriting

python bot.py
```

Agar hammasi to'g'ri bo'lsa, konsolda `Bot ishga tushdi: @sizning_bot_nomi` degan yozuv chiqadi.

---

## 3️⃣ Render.com ga joylash (24/7 ishlashi uchun)

1. Ushbu papkani GitHub'ga yuklang (yangi repository yarating va push qiling).
2. [render.com](https://render.com) ga kiring → **New** → **Web Service**.
3. GitHub repository'ingizni tanlang.
4. Quyidagilarni kiriting:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
5. **Environment Variables** bo'limiga o'ting va qo'shing:
   - `BOT_TOKEN` = sizning bot tokeningiz
   - `ADMIN_IDS` = sizning Telegram ID raqamingiz (bir nechta bo'lsa vergul bilan: `111,222`)
6. **Create Web Service** tugmasini bosing. Render avtomatik build qilib, botni ishga tushiradi.

> ⚠️ **Muhim eslatma**: Render'ning bepul tarifida disk vaqtinchalik (ephemeral) —
> ya'ni har safar qayta deploy qilinganda `bot_database.db` fayli **tozalanishi** mumkin
> (barcha buyurtmalar, foydalanuvchilar, sozlamalar o'chib ketadi). Agar bu muhim bo'lsa:
> - Render'da **Persistent Disk** qo'shing (pullik reja) va `DB_PATH` ni shu diskka
>   yo'naltiring, YOKI
> - Kelajakda PostgreSQL kabi tashqi ma'lumotlar bazasiga o'tkazish tavsiya etiladi.
>
> Oddiy qayta ishga tushirish (restart, uxlab qolgandan uyg'onish) paytida esa fayl saqlanib qoladi —
> faqat **yangi deploy** paytida tozalanish xavfi bor.

Bot polling rejimida ishlaydi (webhook emas), shu bilan birga Render talab qiladigan
portni tinglash uchun ichida oddiy HTTP server ham ishga tushadi — buni o'zgartirish shart emas.

---

## 4️⃣ Botdan foydalanish

### Oddiy foydalanuvchi uchun asosiy tugmalar:
- **💎 Gemini Pro sotib olish** — miqdorni (1–10) tanlab, to'lov qiladi
- **🎬 AI Videolar kanali** — kanal narxini to'lab, linkni oladi
- **ℹ️ Gemini nima?** — obunaga nimalar kirishi haqida ma'lumot
- **📖 Yo'riqnoma** — botdan qanday foydalanish
- **👥 Referal dasturi** — do'stlarni taklif qilish linki
- **💬 Izohlar** — izoh yozish / boshqalarning izohlarini ko'rish
- **🆘 Yordam** — admin bilan bog'lanish

### To'lov jarayoni:
1. Foydalanuvchi mahsulotni tanlaydi → karta raqami va summa chiqadi.
2. To'lovni qilib, **"✅ To'lov qildim"** tugmasini bosadi.
3. Barcha adminlarga xabar keladi: **"✅ Tasdiqlash"** / **"❌ Rad etish"** tugmalari bilan.
4. Agar **kanal** buyurtmasi bo'lsa — link avtomatik yuboriladi.
5. Agar **Gemini Pro** buyurtmasi bo'lsa — bot admindan linkni so'raydi,
   admin linkni yuborgach, bot uni foydalanuvchiga yetkazadi.

### Admin panel (**⚙️ Admin panel** tugmasi):
- 💳 Karta raqami / 👤 Karta egasini o'zgartirish
- 💰 Gemini narxi / 💰 Kanal narxini o'zgartirish
- 🔗 Kanal linkini o'zgartirish
- 🆘 Yordam nikini o'zgartirish
- 📢 Majburiy obuna kanalini o'zgartirish
- ℹ️ "Gemini nima?" matnini o'zgartirish
- 📖 Yo'riqnoma matnini o'zgartirish
- 🎉 Referal xabari matnini o'zgartirish (`{user}` va `{count}` o'zgaruvchilaridan foydalaning)
- 📢 Reklama yuborish — barcha foydalanuvchilarga xabar (matn/rasm/video) yuborish
- 📊 Statistika — foydalanuvchilar soni, sotuvlar, umumiy tushum
- 💬 Izohlarni ko'rish

Har bir sozlashda pastda **"❌ Bekor qilish"** tugmasi chiqib turadi.

---

## 5️⃣ Referal tizimi qanday ishlaydi

- Har bir foydalanuvchi o'zining referal havolasiga ega: `https://t.me/BOT_USERNAME?start=ref_USER_ID`
- Yangi foydalanuvchi shu havola orqali botga kirsa, referal egasining hisobiga +1 qo'shiladi.
- Har 10 ta yangi referalda **barcha adminlarga** avtomatik tabrik xabari yuboriladi
  (matnini admin panelda o'zgartirish mumkin).

---

## ❗ Muhim eslatmalar

- Bot `@aivora_uz` kanaliga a'zo bo'lmagan foydalanuvchilar uchun ishlamaydi
  (bu ham admin panelda o'zgartiriladi).
- Admin panel faqat `ADMIN_IDS` ro'yxatidagi Telegram ID'larga ochiq.
- Botni ikki joyda (masalan lokal + Render) bir vaqtda ishga tushirmang —
  Telegram polling rejimida bitta bot faqat bitta joyda ishlashi kerak, aks holda xatolik chiqadi.
