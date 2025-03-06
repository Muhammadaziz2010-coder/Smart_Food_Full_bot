# Telegram Bot - Buyurtma Berish Bot

## Loyiha haqida

Bu Telegram bot foydalanuvchilarga osonlik bilan buyurtma berish, manzilni kiritish, o‘z buyurtmalarini ko‘rish va aksiyalardan xabardor bo‘lish imkonini beradi. Bot Python’da `aiogram` kutubxonasi yordamida yozilgan bo‘lib, ma'lumotlar bazasi sifatida `SQLAlchemy` ishlatiladi. Geolokatsiya xizmatlari uchun `geopy` qo‘llaniladi.

## Botning imkoniyatlari

- **Telefon raqamini kiritish**: Botni ishga tushirganda foydalanuvchi telefon raqamini yuborishi kerak.
- **Buyurtma berish**: "Yetkazib berish" yoki "Olib ketish" opsiyalari orqali buyurtma berish mumkin.
- **Manzil kiritish**: Lokatsiya yuborish yoki qo‘lda manzil kiritish imkoniyati.
- **Buyurtmalarni ko‘rish**: Oldingi buyurtmalarni ko‘rish va ularning holatini tekshirish.
- **Aksiyalar**: Mavjud chegirmalar haqida ma'lumot olish.
- **Dasturchi bilan bog‘lanish**: Bot yaratuvchisi bilan aloqa qilish uchun kontaktlar.
- **Orqaga qaytish**: Har qanday bosqichda oldingi qadamga yoki menyuga qaytish.

## Botdan foydalanish

### 1. Botni ishga tushirish
- `/start` buyrug‘ini yuboring.
- Agar yangi foydalanuvchi bo‘lsangiz, telefon raqamingizni yuboring (kontakt sifatida yoki matn sifatida, masalan: `+998901234567`).

### 2. Asosiy menyu
Menyuda quyidagi tugmalar mavjud:
- 🛒 **Buyurtma Berish**: Yangi buyurtma boshlash.
- 🛍️ **Mening buyurtmalarim**: Oldingi buyurtmalarni ko‘rish.
- 💰 **Aksiyalar**: Chegirmalar haqida ma'lumot.
- 💻 **Dasturchi bilan bog‘lanish**: Kontakt ma'lumotlari.
- 👈 **Orqaga**: Oldingi qadamga qaytish.

### 3. Buyurtma berish jarayoni
1. "🛒 Buyurtma Berish" tugmasini bosing.
2. Buyurtma turini tanlang:
   - 🚚 **Yetkazib berish**: Manzil kiritish so‘raladi.
   - 📦 **Olib ketish**: To‘g‘ridan-to‘g‘ri web-ilovaga o‘tadi.
3. **Yetkazib berish** uchun:
   - Lokatsiyangizni yuboring yoki qo‘lda manzil kiriting.
   - Manzilni tasdiqlang ("✅ Tasdiqlash") yoki qayta yuboring ("🔄 Manzilni qayta jo‘natish").
   - Tasdiqlangandan so‘ng web-ilovaga o‘tasiz.

### 4. Orqaga qaytish
- Har qanday bosqichda "👈 Ortga" tugmasi bilan oldingi qadamga qaytishingiz mumkin:
  - Manzil kiritishdan buyurtma turini tanlashga.
  - Buyurtma turidan menyuga.
  - Qo‘lda manzil kiritishdan lokatsiya so‘roviga.

### 5. Buyurtmalar va aksiyalar
- "🛍️ Mening buyurtmalarim": Buyurtma ID, sana, manzil, narx va holatni ko‘rsatadi.
- "💰 Aksiyalar": Chegirma nomlari, tavsifi va foizini ko‘rsatadi.

### 6. Xatoliklar
- Agar xatolik yuz bersa, "⚠️ Xatolik yuz berdi, qayta urinib ko‘ring" xabari chiqadi va admin xabardor qilinadi.

## O‘rnatish va ishga tushirish

### Kerakli kutubxonalar
```bash
pip install aiogram sqlalchemy geopy