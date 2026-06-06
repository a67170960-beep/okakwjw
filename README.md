# 🔍 Username Finder Bot

Telegram-бот для поиска свободных юзернеймов. База из **~400 000+** вариантов с удобной навигацией по инлайн-кнопкам.

---

## ✨ Возможности

| Функция | Описание |
|---|---|
| 📋 Просмотр | Листай 400k+ юзернеймов по 50 штук |
| 🎲 Случайные | Случайная подборка в один клик |
| 🔎 Поиск | Поиск по слову или части слова |
| ⭐ Избранное | Сохраняй понравившиеся юзернеймы |
| 📊 Статистика | Личная статистика просмотров |
| 🔗 Открыть | Прямая ссылка t.me/username |
| ℹ️ Детали | Длина, наличие цифр, рейтинг "крутости" |

---

## 🚀 Установка

### 1. Клонируй/скопируй файлы в папку

```
username_bot/
├── bot.py
├── handlers.py
├── keyboards.py
├── usernames.py
├── database.py
├── requirements.txt
└── .env
```

### 2. Создай виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
# или
venv\Scripts\activate         # Windows
```

### 3. Установи зависимости

```bash
pip install -r requirements.txt
```

### 4. Создай .env файл

```bash
cp .env.example .env
```

Открой `.env` и вставь токен от [@BotFather](https://t.me/BotFather):

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 5. Запусти бота

```bash
python bot.py
```

---

## 📦 Как получить токен

1. Напиши [@BotFather](https://t.me/BotFather) в Telegram
2. Отправь `/newbot`
3. Придумай имя и юзернейм для бота
4. Скопируй токен в `.env`

---

## 🌐 Запуск на сервере (systemd)

Создай файл `/etc/systemd/system/username_bot.service`:

```ini
[Unit]
Description=Telegram Username Finder Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/username_bot
ExecStart=/home/ubuntu/username_bot/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable username_bot
sudo systemctl start username_bot
sudo systemctl status username_bot
```

---

## ⚠️ Важно

Бот показывает **потенциально свободные** юзернеймы на основе генерации.
Перед регистрацией обязательно проверь: открой ссылку `t.me/username` — если страница пуста, юзернейм свободен.

Telegram API не позволяет проверять занятость юзернеймов без авторизации аккаунта.

---

## 📊 Статистика базы

- ~400 000+ уникальных юзернеймов
- Длина: 5–20 символов
- Категории: природа, технологии, крипто, игры, общие
- Форматы: word+word, prefix+noun, noun+number и др.
