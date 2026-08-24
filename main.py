import os
import sqlite3
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot import types

TOKEN = "8957204394:AAFasf98ogRUBD4zYnyszlaCor_-3FkXwlw"
WEB_APP_URL = "https://abdulborimusaev0122-hub.github.io/tictactoe/"

bot = telebot.TeleBot(TOKEN)
DB_NAME = "tictactoe.db"

# Простой веб-сервер для бесплатного тарифа Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Инициализация БД
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 100,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            equipped_x TEXT DEFAULT '❌',
            equipped_o TEXT DEFAULT '⭕',
            last_active INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_or_create_user(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    current_time = int(time.time())
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, last_active)
        VALUES (?, ?, ?)
    ''', (user_id, username, current_time))
    
    cursor.execute('''
        UPDATE users 
        SET last_active = ?, username = ? 
        WHERE user_id = ?
    ''', (current_time, username, user_id))
    
    conn.commit()
    cursor.execute('SELECT balance, wins, losses, draws, equipped_x, equipped_o FROM users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

init_db()

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Игрок"
    username = message.from_user.username or first_name
    
    get_or_create_user(user_id, username)
    
    markup = types.InlineKeyboardMarkup()
    btn_app = types.InlineKeyboardButton("🎮 Играть в Крестики-Нолики ❌⭕", web_app=types.WebAppInfo(url=WEB_APP_URL))
    markup.add(btn_app)
    
    text = (
        f"👋 <b>Привет, {first_name}!</b>\n\n"
        f"Добро пожаловать в <b>Крестики-Нолики Arcade</b>! 🏆\n\n"
        f"✨ <b>В игре тебя ждёт:</b>\n"
        f"🤖 Игра против умного ИИ\n"
        f"⚔️ Дуэли с другими игроками\n"
        f"🛍️ Магазин крутых скинов\n"
        f"🪙 Накопление монет и Топ лидеров\n\n"
        f"👇 <i>Нажми на кнопку ниже, чтобы начать!</i>"
    )
    
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)

if __name__ == "__main__":
    # Запускаем фоновый веб-сервер для Render
    threading.Thread(target=run_health_check_server, daemon=True).start()
    print("Бот с Mini App успешно запущен 24/7...")
    bot.infinity_polling()
  
