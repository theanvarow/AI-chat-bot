import asyncio
import os
import base64
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from openai import OpenAI
from pydub import AudioSegment

# API kalitlari
TELEGRAM_TOKEN = ".."
OPENAI_API_KEY = ".."

# OpenAI va Telegram botini sozlash
client = OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Global o‘zgaruvchilar
current_language = "ru"  # Boshlang‘ich til: rus
chat_histories = {}  # Har bir foydalanuvchi uchun suhbat tarixi

# Tilga mos xabarlar
def get_message(lang, key):
    messages = {
        "ru": {
            "start": "👋 Привет! Я бот с функциями ChatGPT. Выбери действие из меню:",
            "menu": "📋 Главное меню:",
            "education": "📚 Раздел 'Обучение'. Выбери подкатегорию:",
            "subscriptions": "💳 Раздел 'Подписки'. Выбери подкатегорию:",
            "settings": "⚙️ Раздел 'Настройки'. Выбери подкатегорию:",
            "back": "🔙 Возвращаемся в главное меню:",
            "language_select": "🌐 Выберите язык интерфейса:",
            "support": "ℹ Раздел 'Поддержка'. Выбери подкатегорию:",
            "chat_history": "📜 История чата:",
            "clear_history": "🗑 Очистить историю чата",
            "subscriptions_info": (
                "📋 **Тарифы и услуги AI** 📋\n"
                "💡 *Ваш лучший помощник!*\n\n"
                "1️⃣ **Обычный режим (Бесплатно)** 🆓\n"
                "- ✅ Ответы на простые вопросы\n"
                "- ❌ Решение задач\n"
                "- ❌ Генерация текстов\n"
                "- ❌ Проверка грамматики\n"
                "- ❌ Анализ данных\n"
                "- ❌ Автоматизация\n"
                "- ❌ Голосовой ввод\n"
                "- ❌ Генерация изображений\n\n"
                "2️⃣ **AI для Учёбы (65,000)** 🎓\n"
                "- ✅ Учебные вопросы\n"
                "- ✅ Математика, физика, химия\n"
                "- ✅ Конспекты, шпаргалки\n"
                "- ✅ Орфография и стилистика\n"
                "- ❌ Анализ данных\n"
                "- ❌ Автоматизация\n"
                "- ❌ Голосовой ввод\n"
                "- ❌ Генерация изображений\n\n"
                "3️⃣ **AI для Бизнеса (85,000)** 💼\n"
                "- ✅ Учебные + бизнес-вопросы\n"
                "- ✅ Анализ и расчёты\n"
                "- ✅ Продающие тексты, бизнес-планы\n"
                "- ✅ Полная редактура\n"
                "- ✅ Базовый анализ рынка\n"
                "- ✅ Ответы на письма, отчёты\n"
                "- ❌ Голосовой ввод\n"
                "- ❌ Генерация изображений\n\n"
                "4️⃣ **AI Премиум (100,000)** 🌟\n"
                "- ✅ Индивидуальный разбор\n"
                "- ✅ Автоматизированный анализ\n"
                "- ✅ Презентации, статьи\n"
                "- ✅ Продвинутая редактура\n"
                "- ✅ Расширенный анализ и прогнозы\n"
                "- ✅ Интеграция с CRM, Google Docs\n"
                "- ✅ Диктовка и голосовые ответы\n"
                "- ✅ Создание картинок и графиков\n\n"
                "📩 *Выберите подходящий тариф и начните прямо сейчас!*\n"
                "🔥 С Премиумом откройте максимум возможностей!"
            ),
            "education_options": {
                "📚 Мои курсы": "📖 Здесь вы можете посмотреть свои активные курсы.",
                "📆 Расписание": "🕒 Ваше расписание занятий доступно здесь.",
                "🎯 Тесты и упражнения": "✅ Пройдите тесты и выполните упражнения.",
                "🎙 Практика устной речи": "🎤 Начните практику устной речи.",
                "📝 Письменные задания": "✍️ Выполните письменные задания."
            },
            "subscriptions_options": {
                "🔄 Оформить подписку": "💡 Оформите подписку для доступа к курсам.",
                "📜 Мои подписки": "📋 Список ваших активных подписок.",
                "💳 Оплата": "💰 Выберите способ оплаты.",
                "📋 Тарифы": "📋 Посмотрите доступные тарифы и их возможности."
            },
            "settings_options": {
                "🔔 Уведомления": "🔔 Настройте уведомления.",
                "🌐 Язык интерфейса": "🌐 Выберите язык интерфейса.",
                "💾 История чатов": "💾 Просмотрите историю чатов."
            },
            "support_options": {
                "📩 Написать в поддержку": "📩 Напишите нам для получения помощи!",
                "❓ FAQ": "❓ Ознакомьтесь с часто задаваемыми вопросами.",
                "🔹 Обратная связь": "🔹 Оставьте свои предложения или отзывы."
            }
        },
        "uz": {
            "start": "👋 Salom! Men ChatGPT funksiyalari bilan botman. Menyudan harakatni tanlang:",
            "menu": "📋 Asosiy menyudir:",
            "education": "📚 'Ta'lim' bo'limi. Kategoriyani tanlang:",
            "subscriptions": "💳 'Obunalar' bo'limi. Kategoriyani tanlang:",
            "settings": "⚙️ 'Sozlamalar' bo'limi. Kategoriyani tanlang:",
            "back": "🔙 Asosiy menyuga qaytamiz:",
            "language_select": "🌐 Interfeys tilini tanlang:",
            "support": "ℹ 'Yordam' bo'limi. Kategoriyani tanlang:",
            "chat_history": "📜 Suhbat tarixi:",
            "clear_history": "🗑 Suhbat tarixini tozalash",
            "subscriptions_info": (
                "📋 **AI xizmatlari va tariflar** 📋\n"
                "💡 *Siz uchun eng yaxshi yordamchi!*\n\n"
                "1️⃣ **Обычный режим (Бесплатно)** 🆓\n"
                "- ✅ Oddiy savollarga javob\n"
                "- ❌ Vazifalarni yechish\n"
                "- ❌ Matn generatsiyasi\n"
                "- ❌ Grammatik tekshiruv\n"
                "- ❌ Ma'lumotlar tahlili\n"
                "- ❌ Avtomatlashtirish\n"
                "- ❌ Ovozli kiritish\n"
                "- ❌ Rasm generatsiyasi\n\n"
                "2️⃣ **AI для Учёбы (65,000)** 🎓\n"
                "- ✅ O‘quv savollarga javob\n"
                "- ✅ Matematika, fizika, kimyo masalalari\n"
                "- ✅ Konspektlar, shpargalkalar\n"
                "- ✅ Orfografiya va stilistik tekshiruv\n"
                "- ❌ Ma'lumotlar tahlili\n"
                "- ❌ Avtomatlashtirish\n"
                "- ❌ Ovozli kiritish\n"
                "- ❌ Rasm generatsiyasi\n\n"
                "3️⃣ **AI для Бизнеса (85,000)** 💼\n"
                "- ✅ O‘quv + biznes savollari\n"
                "- ✅ Tahlil va hisob-kitoblar\n"
                "- ✅ Sotuv matnlari, biznes-rejalar\n"
                "- ✅ To‘liq matn tahriri\n"
                "- ✅ Asosiy bozor tahlili\n"
                "- ✅ Xatlarga javob, hisobotlar\n"
                "- ❌ Ovozli kiritish\n"
                "- ❌ Rasm generatsiyasi\n\n"
                "4️⃣ **AI Премиум (100,000)** 🌟\n"
                "- ✅ Individual tahlil va javoblar\n"
                "- ✅ Avtomatlashtirilgan tahlil\n"
                "- ✅ Prezentatsiyalar, maqolalar\n"
                "- ✅ Ilg‘or matn tahriri\n"
                "- ✅ Kengaytirilgan tahlil va prognozlar\n"
                "- ✅ CRM va Google Docs bilan integratsiya\n"
                "- ✅ Ovozli diktovka va javoblar\n"
                "- ✅ Rasmlar va grafiklar yaratish\n\n"
                "📩 *O‘zingizga mos tarifni tanlang va hoziroq boshlang!*\n"
                "🔥 Premium bilan imkoniyatlaringizni maksimum darajada oshiring!"
            ),
            "education_options": {
                "📚 Mening kurslarim": "📖 Bu yerda faol kurslaringizni ko'rishingiz mumkin.",
                "📆 Jadval": "🕒 Dars jadvalingiz shu yerda.",
                "🎯 Testlar va mashqlar": "✅ Testlarni o'ting va mashqlarni bajaring.",
                "🎙 Og'zaki nutq mashqi": "🎤 Og'zaki nutq mashqini boshlang.",
                "📝 Yozma topshiriqlar": "✍️ Yozma topshiriqlarni bajaring."
            },
            "subscriptions_options": {
                "🔄 Obuna rasmiyatsizlantirish": "💡 Kurslarga kirish uchun obunani ro'yxatdan o'tkazing.",
                "📜 Mening obunalarim": "📋 Faol obunalar ro'yxati.",
                "💳 To‘lov": "💰 To'lov usulini tanlang.",
                "📋 Tariflar": "📋 Mavjud tariflar va ularning imkoniyatlarini ko'ring."
            },
            "settings_options": {
                "🔔 Bildirishnomalar": "🔔 Bildirishnomalarni sozlang.",
                "🌐 Interfeys tili": "🌐 Interfeys tilini tanlang.",
                "💾 Suhbat tarixi": "💾 Suhbat tarixini ko'ring."
            },
            "support_options": {
                "📩 Yordamga yozish": "📩 Yordam olish uchun bizga yozing!",
                "❓ FAQ": "❓ Ko‘p beriladigan savollar bilan tanishing.",
                "🔹 Fikr bildirish": "🔹 Taklif yoki fikrlaringizni qoldiring."
            }
        }
    }
    return messages[lang][key]

# Inline tugmalar yaratish funksiyasi
def create_inline_keyboard(buttons, lang):
    builder = InlineKeyboardBuilder()
    for row in buttons:
        builder.row(*[InlineKeyboardButton(text=btn, callback_data=btn) for btn in row])
    return builder.as_markup()

# Inline menyular
main_menu_buttons = {
    "ru": [
        ["📝 Обучение", "📚 Подписки"],
        ["💬 Чат с ИИ", "🎨 Создать изображение"],
        ["⚙️ Настройки", "ℹ️ Помощь"],
        ["📜 История чата", "🗑 Очистить историю"]
    ],
    "uz": [
        ["📝 Ta'lim", "📚 Obunalar"],
        ["💬 AI suhbat", "🎨 Rasm yaratish"],
        ["⚙️ Sozlamalar", "ℹ️ Yordam"],
        ["📜 Suhbat tarixi", "🗑 Tarixni tozalash"]
    ]
}

education_menu_buttons = {
    "ru": [
        ["📚 Мои курсы", "📆 Расписание"],
        ["🎯 Тесты и упражнения", "🎙 Практика устной речи"],
        ["📝 Письменные задания", "🔙 Назад"]
    ],
    "uz": [
        ["📚 Mening kurslarim", "📆 Jadval"],
        ["🎯 Testlar va mashqlar", "🎙 Og'zaki nutq mashqi"],
        ["📝 Yozma topshiriqlar", "🔙 Orqaga"]
    ]
}

subscriptions_menu_buttons = {
    "ru": [
        ["🔄 Оформить подписку"],
        ["📜 Мои подписки", "💳 Оплата"],
        ["📋 Тарифы"],
        ["🔙 Назад"]
    ],
    "uz": [
        ["🔄 Obuna rasmiyatsizlantirish"],
        ["📜 Mening obunalarim", "💳 To‘lov"],
        ["📋 Tariflar"],
        ["🔙 Orqaga"]
    ]
}

settings_menu_buttons = {
    "ru": [
        ["🔔 Уведомления"],
        ["🌐 Язык интерфейса", "💾 История чатов"],
        ["🔙 Назад"]
    ],
    "uz": [
        ["🔔 Bildirishnomalar"],
        ["🌐 Interfeys tili", "💾 Suhbat tarixi"],
        ["🔙 Orqaga"]
    ]
}

support_menu_buttons = {
    "ru": [
        ["📩 Написать в поддержку"],
        ["❓ FAQ", "🔹 Обратная связь"],
        ["🔙 Назад"]
    ],
    "uz": [
        ["📩 Yordamga yozish"],
        ["❓ FAQ", "🔹 Fikr bildirish"],
        ["🔙 Orqaga"]
    ]
}

language_menu_buttons = [
    ["🇺🇿 O'zbekcha", "🇷🇺 Русский"],
    ["🔙 Назад"]
]

# 🔹 Funksiya: Rasmni Base64 formatga o‘tkazish
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 🔹 Funksiya: Rasmni tahlil qilish (OpenAI Vision API)
async def analyze_image(image_path, user_id):
    base64_image = encode_image(image_path)
    chat_history = chat_histories.get(user_id, [])
    chat_history.append({
        "role": "user",
        "content": [
            {"type": "text", "text": "Ushbu rasmda nima bor?"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
    })
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=chat_history
    )
    result = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": result})
    chat_histories[user_id] = chat_history
    return result

# 🔹 Funksiya: Ovoz faylini matnga aylantirish
async def transcribe_audio(audio_path, user_id):
    audio = AudioSegment.from_file(audio_path)
    audio.export("converted.wav", format="wav")
    with open("converted.wav", "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    text = transcript.text
    chat_history = chat_histories.get(user_id, [])
    chat_history.append({"role": "user", "content": f"[Ovozli xabar transkripsiyasi]: {text}"})
    chat_histories[user_id] = chat_history
    return text

# 🔹 OpenAI bilan suhbat funksiyasi
async def chat_with_openai(user_message, user_id):
    chat_history = chat_histories.get(user_id, [])
    chat_history.append({"role": "user", "content": user_message})
    completion = await asyncio.to_thread(
        client.chat.completions.create,
        model="gpt-4o",
        messages=chat_history
    )
    response_text = completion.choices[0].message.content
    chat_history.append({"role": "assistant", "content": response_text})
    chat_histories[user_id] = chat_history
    return response_text

# 🔹 Kodni chiroyli qilish funksiyasi
def format_code(raw_code: str) -> str:
    if not raw_code or not raw_code.strip():
        return "❌ Kod kiritilmadi!"
    lines = raw_code.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    if not lines:
        return "❌ Kodda hech narsa yo‘q!"
    formatted_code = []
    indent_level = 0
    indent_size = 4
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.endswith(')'):
            indent_level = max(0, indent_level - 1)
        indent = ' ' * (indent_level * indent_size)
        formatted_code.append(indent + stripped_line)
        if '(' in stripped_line and not stripped_line.endswith(')'):
            indent_level += 1
        elif stripped_line.endswith(':'):
            indent_level += 1
    return "```python\n" + '\n'.join(formatted_code) + "\n```"

# 🔹 Tilni o‘zgartirish funksiyasi
async def change_language(callback_query: types.CallbackQuery):
    global current_language
    if callback_query.data == "🇺🇿 O'zbekcha":
        current_language = "uz"
    elif callback_query.data == "🇷🇺 Русский":
        current_language = "ru"
    await callback_query.message.edit_text(get_message(current_language, "menu"), reply_markup=create_inline_keyboard(main_menu_buttons[current_language], current_language))
    await callback_query.answer()

# 🔹 Telegram buyruqlari va handlerlar
@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    chat_histories[user_id] = []  # Har bir foydalanuvchi uchun suhbat tarixini boshlash
    await message.answer(get_message(current_language, "start"), reply_markup=create_inline_keyboard(main_menu_buttons[current_language], current_language))

@dp.message(Command("menu"))
async def menu_command(message: types.Message):
    await message.delete()
    await message.answer(get_message(current_language, "menu"), reply_markup=create_inline_keyboard(main_menu_buttons[current_language], current_language))

@dp.message(Command("test_gpt"))
async def test_gpt_command(message: types.Message):
    user_id = message.from_user.id
    completion = await chat_with_openai("Bir jumlali ertak yozing.", user_id)
    await message.answer(completion)

@dp.message(lambda message: message.photo)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    os.makedirs("downloads", exist_ok=True)
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = file.file_path
    image_path = f"downloads/{photo.file_id}.jpg"
    await bot.download_file(file_path, image_path)
    result = await analyze_image(image_path, user_id)
    await message.answer(f"🖼 Rasm tahlili: {result}")

@dp.message(lambda message: message.voice)
async def handle_voice(message: types.Message):
    user_id = message.from_user.id
    os.makedirs("downloads", exist_ok=True)
    voice = message.voice
    file = await bot.get_file(voice.file_id)
    file_path = file.file_path
    audio_path = f"downloads/{voice.file_id}.ogg"
    await bot.download_file(file_path, audio_path)
    result = await transcribe_audio(audio_path, user_id)
    await message.answer(f"🎤 Ovoz tahlili: {result}")
    # Transkripsiyadan keyin suhbatni davom ettirish uchun
    gpt_reply = await chat_with_openai(result, user_id)
    await message.answer(f" {gpt_reply}")

@dp.message(lambda message: message.text.startswith("/format"))
async def format_code_request(message: types.Message):
    user_id = message.from_user.id
    await message.delete()
    raw_code = message.text.replace("/format", "").strip()
    if not raw_code:
        await message.answer("❌ Пожалуйста, отправьте код после команды /format! Например:\n`/format import asyncio`" if current_language == "ru" else 
                            "❌ Iltimos, /format dan keyin kod yuboring! Masalan:\n`/format import asyncio`")
        return
    formatted_code = format_code(raw_code)
    await message.answer("📝 Отформатированный код:\n" + formatted_code)
    chat_histories[user_id].append({"role": "user", "content": f"/format {raw_code}"})
    chat_histories[user_id].append({"role": "assistant", "content": formatted_code})

@dp.message(lambda message: message.text.startswith("/draw"))
async def generate_image(message: types.Message):
    user_id = message.from_user.id
    await message.delete()
    prompt = message.text.replace("/draw", "").strip()
    if not prompt:
        await message.answer("❌ Пожалуйста, укажите описание изображения! Например:\n`/draw Город под снегом`" if current_language == "ru" else 
                            "❌ Iltimos, rasm tavsifini yozing! Masalan:\n`/draw Qor ostidagi shahar`")
        return
    await message.answer("🎨 Изображение создается... ⏳" if current_language == "ru" else "🎨 Rasm chizilmoqda... ⏳")
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        await message.answer_photo(photo=image_url, caption="✅ Изображение готово!" if current_language == "ru" else "✅ Rasm tayyor!")
        chat_histories[user_id].append({"role": "user", "content": f"/draw {prompt}"})
        chat_histories[user_id].append({"role": "assistant", "content": f"[Rasm generatsiyasi]: {image_url}"})
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}" if current_language == "ru" else f"Xatolik: {str(e)}")

@dp.callback_query(lambda c: c.data in ["📝 Обучение", "📝 Ta'lim"])
async def open_education_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(get_message(current_language, "education"), reply_markup=create_inline_keyboard(education_menu_buttons[current_language], current_language))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data in ["📚 Подписки", "📚 Obunalar"])
async def open_subscriptions_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(get_message(current_language, "subscriptions"), reply_markup=create_inline_keyboard(subscriptions_menu_buttons[current_language], current_language))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data in ["⚙️ Настройки", "⚙️ Sozlamalar"])
async def open_settings_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(get_message(current_language, "settings"), reply_markup=create_inline_keyboard(settings_menu_buttons[current_language], current_language))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data in ["ℹ️ Помощь", "ℹ️ Yordam"])
async def open_support_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(get_message(current_language, "support"), reply_markup=create_inline_keyboard(support_menu_buttons[current_language], current_language))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data in ["🔙 Назад", "🔙 Orqaga"])
async def back_to_main_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(get_message(current_language, "back"), reply_markup=create_inline_keyboard(main_menu_buttons[current_language], current_language))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data in ["🌐 Язык интерфейса", "🌐 Interfeys tili"])
async def open_language_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(get_message(current_language, "language_select"), reply_markup=create_inline_keyboard(language_menu_buttons, current_language))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data in ["🇺🇿 O'zbekcha", "🇷🇺 Русский"])
async def change_language_handler(callback_query: types.CallbackQuery):
    await change_language(callback_query)

@dp.callback_query(lambda c: c.data in ["📜 История чата", "📜 Suhbat tarixi"])
async def show_chat_history(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chat_history = chat_histories.get(user_id, [])
    if not chat_history:
        await callback_query.message.edit_text("📜 История чата пуста." if current_language == "ru" else "📜 Suhbat tarixi bo‘sh.")
    else:
        history_text = get_message(current_language, "chat_history") + "\n\n"
        for msg in chat_history:
            role = "👤 Пользователь" if msg["role"] == "user" else " Бот"
            content = msg["content"]
            if isinstance(content, list):  # Agar rasm bo‘lsa
                content = "[Rasm yuborildi]"
            history_text += f"{role}: {content}\n\n"
        await callback_query.message.edit_text(history_text, reply_markup=create_inline_keyboard(main_menu_buttons[current_language], current_language))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data in ["🗑 Очистить историю", "🗑 Tarixni tozalash"])
async def clear_chat_history(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chat_histories[user_id] = []
    await callback_query.message.edit_text("🗑 История чата очищена." if current_language == "ru" else "🗑 Suhbat tarixi tozalandi.", reply_markup=create_inline_keyboard(main_menu_buttons[current_language], current_language))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data in [
    "📚 Мои курсы", "📆 Расписание", "🎯 Тесты и упражнения", "🎙 Практика устной речи", "📝 Письменные задания",
    "📚 Mening kurslarim", "📆 Jadval", "🎯 Testlar va mashqlar", "🎙 Og'zaki nutq mashqi", "📝 Yozma topshiriqlar"
])
async def handle_education_options(callback_query: types.CallbackQuery):
    option = callback_query.data
    response = get_message(current_language, "education_options").get(option, "Неизвестная опция.")
    await callback_query.message.edit_text(response + "\nВыберите еще: ", reply_markup=create_inline_keyboard(education_menu_buttons[current_language], current_language))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data in ["🔄 Оформить подписку", "📜 Мои подписки", "💳 Оплата", "🔄 Obuna rasmiyatsizlantirish", "📜 Mening obunalarim", "💳 To‘lov", "📋 Тарифы", "📋 Tariflar"])
async def handle_subscriptions_options(callback_query: types.CallbackQuery):
    option = callback_query.data
    if option in ["📋 Тарифы", "📋 Tariflar"]:
        response = get_message(current_language, "subscriptions_info")
    else:
        response = get_message(current_language, "subscriptions_options").get(option, "Неизвестная опция.")
    await callback_query.message.edit_text(response + "\nВыберите еще: ", reply_markup=create_inline_keyboard(subscriptions_menu_buttons[current_language], current_language), parse_mode="Markdown")
    await callback_query.answer()

@dp.callback_query(lambda c: c.data in ["🔔 Уведомления", "🌐 Язык интерфейса", "💾 История чатов", "🔔 Bildirishnomalar", "🌐 Interfeys tili", "💾 Suhbat tarixi"])
async def handle_settings_options(callback_query: types.CallbackQuery):
    option = callback_query.data
    response = get_message(current_language, "settings_options").get(option, "Неизвестная опция.")
    await callback_query.message.edit_text(response + "\nВыберите еще: ", reply_markup=create_inline_keyboard(settings_menu_buttons[current_language], current_language))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data in ["📩 Написать в поддержку", "❓ FAQ", "🔹 Обратная связь", "📩 Yordamga yozish", "🔹 Fikr bildirish"])
async def handle_support_options(callback_query: types.CallbackQuery):
    option = callback_query.data
    response = get_message(current_language, "support_options").get(option, "Неизвестная опция.")
    await callback_query.message.edit_text(response + "\nВыберите еще: ", reply_markup=create_inline_keyboard(support_menu_buttons[current_language], current_language))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data in ["💬 Чат с ИИ", "💬 AI suhbat"])
async def ask_gpt(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("✍️ Напишите мне свой вопрос, и я отвечу!" if current_language == "ru" else "✍️ Menga savolingizni yozing, men javob beraman!")
    await callback_query.answer()

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    if message.text and message.text not in ["/start", "/menu", "/format", "/draw", "/test_gpt"]:
        user_message = message.text
        waiting_message = await message.answer("⏳ Ответ пишется... ⌛" if current_language == "ru" else "⏳ Javob yozilmoqda... ⌛")
        gpt_reply = await chat_with_openai(user_message, user_id)
        await bot.delete_message(chat_id=message.chat.id, message_id=waiting_message.message_id)
        await message.answer(f"\n\n{gpt_reply}", parse_mode="Markdown")

# 🔹 Botni ishga tushirish
async def main():
    print("🚀 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())