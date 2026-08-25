import os
import json
import psycopg2
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

TOKEN = os.environ.get("BOT_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")
WEB_APP_URL = "https://abdulborimusaev0122-hub.github.io/tictactoe/"

bot = telebot.TeleBot(TOKEN)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                balance INT DEFAULT 200,
                wins INT DEFAULT 0,
                losses INT DEFAULT 0,
                draws INT DEFAULT 0,
                equipped_x TEXT DEFAULT '❌',
                equipped_o TEXT DEFAULT '⭕'
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка БД: {e}")

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
        self.wfile.write(b"Server is live!")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
            user_id = data.get('user_id')
            balance = data.get('balance', 200)
            wins = data.get('wins', 0)
            losses = data.get('losses', 0)
            draws = data.get('draws', 0)
            equipped_x = data.get('equipped_x', '❌')
            equipped_o = data.get('equipped_o', '⭕')

            if user_id:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (user_id, balance, wins, losses, draws, equipped_x, equipped_o)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        balance = EXCLUDED.balance,
                        wins = EXCLUDED.wins,
                        losses = EXCLUDED.losses,
                        draws = EXCLUDED.draws,
                        equipped_x = EXCLUDED.equipped_x,
                        equipped_o = EXCLUDED.equipped_o;
                ''', (user_id, balance, wins, losses, draws, equipped_x, equipped_o))
                conn.commit()
                cursor.close()
                conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            self.send_response(500)
            self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), WebAppRequestHandler)
    server.serve_forever()

init_db()

@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = types.InlineKeyboardMarkup()
    btn_app = types.InlineKeyboardButton("🎮 Играть в Крестики-Нолики", web_app=types.WebAppInfo(url=WEB_APP_URL))
    markup.add(btn_app)

    text = f"👋 Привет, {message.from_user.first_name}!\nДобро пожаловать в Крестики-Нолики Arcade! 🏆\n\nНажми на кнопку ниже, чтобы начать:"
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    bot.infinity_polling()
    
