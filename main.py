import os
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot import types
import psycopg2

TюTOKEN = os.environ.get("8957204394:AAFasf98ogRUBD4zYnyszlaCor_-3FkXwlw")
DATABASE_URL = os.environ.get("DATABASE_URL")
WEB_APP_URL = "https://abdulborimusaev0122-hub.github.io/tictactoe/"

bot = telebot.TeleBot(TOKEN)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                balance INTEGER DEFAULT 100,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                equipped_x TEXT DEFAULT '❌',
                equipped_o TEXT DEFAULT '⭕',
                last_active BIGINT DEFAULT 0
            );
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("База данных Supabase успешно инициализирована!")
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")

def get_or_create_user(user_id, username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        current_time = int(time.time())
        cursor.execute('''
            INSERT INTO users (user_id, username, last_active)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id) 
            DO UPDATE SET last_active = EXCLUDED.last_active, username = EXCLUDED.username;
        ''', (user_id, username, current_time))
        conn.commit()
        
        cursor.execute('SELECT balance, wins, losses, draws, equipped_x, equipped_o FROM users WHERE user_id = %s;', (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return user_data
    except Exception as e:
        print(f"Ошибка получения пользователя: {e}")
        return None

def save_user_progress(user_id, balance, wins, losses, draws, equipped_x, equipped_o):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET balance = %s, wins = %s, losses = %s, draws = %s, equipped_x = %s, equipped_o = %s
            WHERE user_id = %s;
        ''', (balance, wins, losses, draws, equipped_x, equipped_o, user_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка сохранения прогресса: {e}")

class WebAppRequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b"Server and Database are live!")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            user_id = data.get('user_id')
            balance = data.get('balance', 100)
            wins = data.get('wins', 0)
            losses = data.get('losses', 0)
            draws = data.get('draws', 0)
            equipped_x = data.get('equipped_x', '❌')
            equipped_o = data.get('equipped_o', '⭕')
            
            if user_id:
                save_user_progress(user_id, balance, wins, losses, draws, equipped_x, equipped_o)
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), WebAppRequestHandler)
    server.serve_forever()

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
        f"👇 <i>Нажми на кнопку ниже, чтобы начать!</i>"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    print("Бот и API сохранения успешно запущены 24/7...")
    bot.infinity_polling()
            
