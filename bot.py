import telebot
import sqlite3
import time
from datetime import datetime

TOKEN = "9242485782:AAGU5_BGCT7h49F35sHA41fbZtmM7JppNHc"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Укажи здесь свой Telegram ID цифрами для доступа к админке
ADMIN_ID = 123456789  

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS user_nicks (user_id INTEGER, nick TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS blocked_users (user_id INTEGER UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS servers (server_name TEXT UNIQUE)")
    
    default_servers = ["Texas", "Florida", "Nevada", "Hawaii", "Indiana"]
    for s in default_servers:
        cursor.execute("INSERT OR IGNORE INTO servers (server_name) VALUES (?)", (s,))
        
    conn.commit()
    conn.close()

init_db()

# --- КОМАНДА /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blocked_users WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        conn.close()
        bot.send_message(user_id, "❌ Вы заблокированы в этом боте.")
        return
    conn.close()

    text = (
        "👋 <b>Добро пожаловать в бот мониторинга серверов проекта ONLINE RP!</b>\n\n"
        "👨‍💻 <b>Создатель бота:</b> Заместитель Главного администратора 2-го сервера — Michael Henderson.\n\n"
        "🎯 <b>Назначение бота:</b>\n"
        "Отслеживание ваших игровых аккаунтов на серверах проекта ONLINE RP.\n"
        "Если кто-то зайдёт под вашим ником на сервер, вы мгновенно получите уведомление.\n\n"
        "📋 <b>Ваши команды:</b>\n"
        "• <code>/ник добавить &lt;ник&gt;</code> — добавить свой ник для отслеживания\n"
        "• <code>/ник убрать &lt;ник&gt;</code> — убрать ник из отслеживания\n"
        "• <code>/ник список</code> — показать свои отслеживаемые ники\n"
        "• <code>/сервер список</code> — показать сервера под мониторингом\n"
        "• <code>/статистика</code> — ваша статистика за текущие сутки\n"
        "• <code>/помощь</code> — эта справка\n\n"
        "🔒 <i>У каждого пользователя свои ники и статистика.</i>\n\n"
        "⚠️ <b>Если есть проблемы или замечания по боту:</b>\n"
        "Свяжитесь со мной через форум проекта или VK:\n"
        "https://vk.com/fant1k71\n\n"
        "<b>Удачной игры в ONLINE RP! 🎮</b>"
    )
    bot.send_message(message.chat.id, text)

# --- КОМАНДА /помощь ---
@bot.message_handler(commands=['помощь'])
def send_help(message):
    text = (
        "🤖 <b>Бот мониторинга SA-MP серверов</b>\n\n"
        "<b>Доступные команды:</b>\n"
        "• <code>/ник добавить &lt;ник&gt;</code> — добавить свой ник в отслеживание\n"
        "• <code>/ник убрать &lt;ник&gt;</code> — убрать ник из отслеживания\n"
        "• <code>/ник список</code> — показать свои отслеживаемые ники\n"
        "• <code>/сервер список</code> — показать сервера под мониторингом\n"
        "• <code>/статистика</code> — своя статистика за текущие сутки\n"
        "• <code>/помощь</code> — эта справка\n\n"
    )
    
    if message.from_user.id == ADMIN_ID:
        text += (
            "👑 <b>Команды владельца бота:</b>\n"
            "• <code>/сервер добавить &lt;Имя&gt;</code> — добавить сервер\n"
            "• <code>/сервер удалить &lt;Имя&gt;</code> — убрать сервер\n"
            "• <code>/блокировка добавить &lt;ID&gt;</code> — заблокировать пользователя\n"
            "• <code>/блокировка убрать &lt;ID&gt;</code> — разблокировать\n"
            "• <code>/блокировка список</code> — список заблокированных\n"
            "• <code>/пользователи</code> — список всех пользователей\n"
            "• <code>/рассылка &lt;текст&gt;</code> — отправить сообщение всем\n\n"
        )
        
    text += "🔒 <i>У каждого пользователя свои ники и статистика.</i>"
    bot.send_message(message.chat.id, text)

# --- УПРАВЛЕНИЕ НИКАМИ ---
@bot.message_handler(commands=['ник'])
def handle_nicks(message):
    args = message.text.split()
    user_id = message.chat.id
    
    if len(args) < 2:
        bot.send_message(user_id, "❌ <b>Использование:</b> <code>/ник добавить &lt;ник&gt;</code> или <code>/ник убрать &lt;ник&gt;</code>")
        return
        
    action = args[1].lower()
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    
    if action == "добавить" and len(args) >= 3:
        nick = args[2]
        cursor.execute("SELECT * FROM user_nicks WHERE user_id = ? AND nick = ?", (user_id, nick))
        if cursor.fetchone():
            bot.send_message(user_id, "⚠️ Ник <b>" + nick + "</b> уже находится в вашем списке отслеживания.")
        else:
            cursor.execute("INSERT INTO user_nicks (user_id, nick) VALUES (?, ?)", (user_id, nick))
            conn.commit()
            bot.send_message(user_id, "✅ Ник <b>" + nick + "</b> добавлен в ваше отслеживание.")
            
    elif action == "убрать" and len(args) >= 3:
        nick = args[2]
        cursor.execute("DELETE FROM user_nicks WHERE user_id = ? AND nick = ?", (user_id, nick))
        conn.commit()
        bot.send_message(user_id, "🗑 Ник <b>" + nick + "</b> удален из отслеживания.")
        
    elif action == "список":
        cursor.execute("SELECT nick FROM user_nicks WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        if rows:
            nicks_list = ""
            for row in rows:
                nicks_list += "• <code>" + row[0] + "</code>\n"
            bot.send_message(user_id, "📋 <b>Ваши отслеживаемые ники:</b>\n" + nicks_list)
        else:
            bot.send_message(user_id, "⚠️ У вас пока нет добавленных ников для отслеживания.")
    else:
        bot.send_message(user_id, "❌ Неверная команда. Используйте: <code>/ник добавить &lt;ник&gt;</code> или <code>/ник убрать &lt;ник&gt;</code>")
        
    conn.close()

# --- УПРАВЛЕНИЕ СЕРВЕРАМИ ---
@bot.message_handler(commands=['сервер'])
def handle_servers(message):
    args = message.text.split()
    user_id = message.chat.id
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    
    if len(args) >= 2 and args[1].lower() == "список":
        cursor.execute("SELECT server_name FROM servers")
        rows = cursor.fetchall()
        servers_list = ""
        for row in rows:
            servers_list += "• 🌐 " + row[0] + "\n"
        bot.send_message(user_id, "📌 <b>Доступные сервера под мониторингом:</b>\n" + servers_list)
        
    elif len(args) >= 3 and args[1].lower() == "добавить" and message.from_user.id == ADMIN_ID:
        srv = args[2]
        try:
            cursor.execute("INSERT INTO servers (server_name) VALUES (?)", (srv,))
            conn.commit()
            bot.send_message(user_id, "✅ Сервер <b>" + srv + "</b> добавлен в мониторинг.")
        except:
            bot.send_message(user_id, "⚠️ Сервер <b>" + srv + "</b> уже существует.")
            
    elif len(args) >= 3 and args[1].lower() == "удалить" and message.from_user.id == ADMIN_ID:
        srv = args[2]
        cursor.execute("DELETE FROM servers WHERE server_name = ?", (srv,))
        conn.commit()
        bot.send_message(user_id, "🗑 Сервер <b>" + srv + "</b> удален из мониторинга.")
    else:
        bot.send_message(user_id, "❌ Использование: <code>/сервер список</code>")
        
    conn.close()

# --- СТАТИСТИКА ---
@bot.message_handler(commands=['статистика'])
def handle_stats(message):
    user_id = message.chat.id
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM user_nicks WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    
    today = datetime.now().strftime("%d.%m.%Y")
    text = (
        "📊 <b>Ваша статистика за текущие сутки (" + today + "):</b>\n\n"
        "• Активных ников в отслеживании: <b>" + str(count) + "</b>\n"
        "• Статус системы: 🟢 Работает стабильно"
    )
    bot.send_message(user_id, text)

# --- АДМИНКА ---
@bot.message_handler(commands=['блокировка'])
def handle_block(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    
    if len(args) >= 3 and args[1].lower() == "добавить":
        target_id = args[2]
        cursor.execute("INSERT OR IGNORE INTO blocked_users (user_id) VALUES (?)", (target_id,))
        conn.commit()
        bot.send_message(message.chat.id, "🚫 Пользователь <code>" + target_id + "</code> заблокирован.")
    elif len(args) >= 3 and args[1].lower() == "убрать":
        target_id = args[2]
        cursor.execute("DELETE FROM blocked_users WHERE user_id = ?", (target_id,))
        conn.commit()
        bot.send_message(message.chat.id, "✅ Пользователь <code>" + target_id + "</code> разблокирован.")
    elif len(args) >= 2 and args[1].lower() == "список":
        cursor.execute("SELECT user_id FROM blocked_users")
        rows = cursor.fetchall()
        blocked_list = ""
        for r in rows:
            blocked_list += str(r[0]) + "\n"
        if not blocked_list:
            blocked_list = "Список пуст"
        bot.send_message(message.chat.id, "📋 <b>Заблокированные ID:</b>\n" + blocked_list)
    conn.close()

@bot.message_handler(commands=['пользователи'])
def handle_users(message):
    if message.from_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM user_nicks")
    rows = cursor.fetchall()
    users_list = ""
    for r in rows:
        users_list += str(r[0]) + "\n"
    if not users_list:
        users_list = "Нет пользователей с никами"
    conn.close()
    bot.send_message(message.chat.id, "👥 <b>Пользователи с никами:</b>\n" + users_list)

@bot.message_handler(commands=['рассылка'])
def handle_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    text_to_send = message.text.replace("/рассылка", "").strip()
    if not text_to_send:
        bot.send_message(message.chat.id, "❌ Укажите текст для рассылки.")
        return
        
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM user_nicks")
    users = cursor.fetchall()
    conn.close()
    
    success = 0
    for u in users:
        try:
            bot.send_message(u[0], "📢 <b>Рассылка от Администрации:</b>\n\n" + text_to_send)
            success += 1
        except:
            pass
            
    bot.send_message(message.chat.id, "✅ Рассылка завершена. Успешно отправлено: " + str(success) + " пользователям.")

# --- СТАБИЛЬНЫЙ ЗАПУСК БЕЗ ЗАВИСАНИЙ ---
if __name__ == "__main__":
    print("Бот запускается в стабильном режиме...")
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            print("Ошибка соединения, переподключение через 3 секунды...", e)
            time.sleep(3)
