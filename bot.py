import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import sqlite3
from datetime import datetime, date, timedelta, time
import json
import asyncio
from aiohttp import web
import hmac
import hashlib
from urllib.parse import parse_qs, unquote

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== SOZLAMALAR ==================
BOT_TOKEN = "8306832040:AAFUo13FORfelJhKNzuM8-WTG5DX6aGThJg"
WEB_APP_URL = "https://nodirbek-code.github.io/ramazon_web_app/"
ADMIN_ID = 6223402432

# Ramazon boshlanish sanasi
RAMADAN_START_DATE = date(2026, 2, 19)  # 19 Fevral 2026

# Video IDs
INTRO_VIDEO_ID = "BAACAgQAAxkBAAICQ2mVt6eepokOXLb2E-umY-ClWvc0AALiCgAC9eudUJSq6GTe3RPvOgQ"
RAMADAN_VIDEO_ID = "BAACAgQAAxkBAAICRWmVt8or6FSb73ay8aHy4qzqgu7wAAJuCgAC6bmkULzCE5f64XCkOgQ"

# Taqvim rasmlari
CALENDAR_IMAGES = {
    "Toshkent": "AgACAgIAAxkBAAIBeWmUt4-u9zwDPATyuSVKrG4ubl4UAAKTGmsb6GupSJuIFSWZM-uIAQADAgADeQADOgQ",
    "Urganch": "AgACAgIAAxkBAAIBfWmUuRk84RQ03vVM_jLKORIfUdZfAAKhGmsb6GupSCFK2qKKgw-pAQADAgADeQADOgQ",
    "Shovot": "AgACAgIAAxkBAAIBfWmUuRk84RQ03vVM_jLKORIfUdZfAAKhGmsb6GupSCFK2qKKgw-pAQADAgADeQADOgQ",
}

# ================== VAQTLAR ==================
TOSHKENT_TIMES = [
    {"saharlik": "05:54", "iftor": "18:05"},
    {"saharlik": "05:53", "iftor": "18:07"},
    {"saharlik": "05:51", "iftor": "18:08"},
    {"saharlik": "05:50", "iftor": "18:09"},
    {"saharlik": "05:49", "iftor": "18:10"},
    {"saharlik": "05:47", "iftor": "18:11"},
    {"saharlik": "05:46", "iftor": "18:13"},
    {"saharlik": "05:44", "iftor": "18:14"},
    {"saharlik": "05:43", "iftor": "18:15"},
    {"saharlik": "05:41", "iftor": "18:16"},
    {"saharlik": "05:40", "iftor": "18:17"},
    {"saharlik": "05:38", "iftor": "18:19"},
    {"saharlik": "05:37", "iftor": "18:20"},
    {"saharlik": "05:35", "iftor": "18:21"},
    {"saharlik": "05:34", "iftor": "18:22"},
    {"saharlik": "05:32", "iftor": "18:23"},
    {"saharlik": "05:31", "iftor": "18:24"},
    {"saharlik": "05:29", "iftor": "18:25"},
    {"saharlik": "05:27", "iftor": "18:27"},
    {"saharlik": "05:26", "iftor": "18:28"},
    {"saharlik": "05:24", "iftor": "18:29"},
    {"saharlik": "05:22", "iftor": "18:30"},
    {"saharlik": "05:21", "iftor": "18:31"},
    {"saharlik": "05:19", "iftor": "18:32"},
    {"saharlik": "05:17", "iftor": "18:33"},
    {"saharlik": "05:15", "iftor": "18:34"},
    {"saharlik": "05:14", "iftor": "18:35"},
    {"saharlik": "05:12", "iftor": "18:37"},
    {"saharlik": "05:10", "iftor": "18:38"},
    {"saharlik": "05:08", "iftor": "18:39"},
]

URGANCH_TIMES = [
    {"saharlik": "06:29", "iftor": "18:40"},
    {"saharlik": "06:27", "iftor": "18:41"},
    {"saharlik": "06:26", "iftor": "18:42"},
    {"saharlik": "06:25", "iftor": "18:43"},
    {"saharlik": "06:23", "iftor": "18:44"},
    {"saharlik": "06:22", "iftor": "18:46"},
    {"saharlik": "06:20", "iftor": "18:47"},
    {"saharlik": "06:19", "iftor": "18:48"},
    {"saharlik": "06:17", "iftor": "18:49"},
    {"saharlik": "06:16", "iftor": "18:50"},
    {"saharlik": "06:14", "iftor": "18:52"},
    {"saharlik": "06:13", "iftor": "18:53"},
    {"saharlik": "06:11", "iftor": "18:54"},
    {"saharlik": "06:10", "iftor": "18:55"},
    {"saharlik": "06:08", "iftor": "18:56"},
    {"saharlik": "06:06", "iftor": "18:57"},
    {"saharlik": "06:05", "iftor": "18:59"},
    {"saharlik": "06:03", "iftor": "19:00"},
    {"saharlik": "06:02", "iftor": "19:01"},
    {"saharlik": "06:00", "iftor": "19:02"},
    {"saharlik": "05:58", "iftor": "19:03"},
    {"saharlik": "05:56", "iftor": "19:04"},
    {"saharlik": "05:55", "iftor": "19:05"},
    {"saharlik": "05:53", "iftor": "19:07"},
    {"saharlik": "05:51", "iftor": "19:08"},
    {"saharlik": "05:50", "iftor": "19:09"},
    {"saharlik": "05:48", "iftor": "19:10"},
    {"saharlik": "05:46", "iftor": "19:11"},
    {"saharlik": "05:44", "iftor": "19:12"},
    {"saharlik": "05:43", "iftor": "19:13"},
]

SHOVOT_TIMES = [
    {"saharlik": "06:29", "iftor": "18:40"},
    {"saharlik": "06:27", "iftor": "18:41"},
    {"saharlik": "06:26", "iftor": "18:42"},
    {"saharlik": "06:25", "iftor": "18:43"},
    {"saharlik": "06:23", "iftor": "18:44"},
    {"saharlik": "06:22", "iftor": "18:46"},
    {"saharlik": "06:20", "iftor": "18:47"},
    {"saharlik": "06:19", "iftor": "18:48"},
    {"saharlik": "06:17", "iftor": "18:49"},
    {"saharlik": "06:16", "iftor": "18:50"},
    {"saharlik": "06:14", "iftor": "18:52"},
    {"saharlik": "06:13", "iftor": "18:53"},
    {"saharlik": "06:11", "iftor": "18:54"},
    {"saharlik": "06:10", "iftor": "18:55"},
    {"saharlik": "06:08", "iftor": "18:56"},
    {"saharlik": "06:06", "iftor": "18:57"},
    {"saharlik": "06:05", "iftor": "18:59"},
    {"saharlik": "06:03", "iftor": "19:00"},
    {"saharlik": "06:02", "iftor": "19:01"},
    {"saharlik": "06:00", "iftor": "19:02"},
    {"saharlik": "05:58", "iftor": "19:03"},
    {"saharlik": "05:56", "iftor": "19:04"},
    {"saharlik": "05:55", "iftor": "19:05"},
    {"saharlik": "05:53", "iftor": "19:07"},
    {"saharlik": "05:51", "iftor": "19:08"},
    {"saharlik": "05:50", "iftor": "19:09"},
    {"saharlik": "05:48", "iftor": "19:10"},
    {"saharlik": "05:46", "iftor": "19:11"},
    {"saharlik": "05:44", "iftor": "19:12"},
    {"saharlik": "05:43", "iftor": "19:13"},
]

CITY_TIMES = {
    "Toshkent": TOSHKENT_TIMES,
    "Urganch": URGANCH_TIMES,
    "Shovot": SHOVOT_TIMES
}

# Duolar
SAHARLIK_DUOSI = """
🤲 *Saharlik duosi:*

_Navaytu an asuma sovma shahri ramazona min al-fajri ilal-mag'ribi, xolisan lillahi ta'ala, Allohu akbar!_

*Ma'nosi:* Ramazon oyining ro'zasini subhidan to kun botguncha tutmoqni niyat qildim. Xolis Alloh uchun. Alloh ulug'dir!
"""

IFTOR_DUOSI = """
🤲 *Iftorlik duosi:*

_Allohumma laka sumtu va bika amantu va a'layka tavakkaltu va a'la rizqika aftartu, favg'firli ma qoddamtu va ma axxortu, ya Arhamar-rohimiyn!_

*Ma'nosi:* Ey Alloh! Senga ro'za tutdim, Senga iymon keltirdim, Senga tavakkal qildim va bergan rizqing bilan iftor qildim. Ey mehribonlarning eng mehriboni, mening avvalgi va keyingi gunohlarimni mag'firat qil!
"""


# ================== RAMAZON KUN HISOBLASH ==================
def get_ramadan_day():
    today = date.today()
    if today < RAMADAN_START_DATE:
        return 0
    ramadan_end = RAMADAN_START_DATE + timedelta(days=29)
    if today > ramadan_end:
        return -1
    delta = (today - RAMADAN_START_DATE).days
    return delta + 1


def get_ramadan_date_for_day(day_number):
    return RAMADAN_START_DATE + timedelta(days=day_number - 1)


# ================== DATABASE ==================
class Database:
    def __init__(self, db_file='ramadan_final.db'):
        self.db_file = db_file
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_file)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                city TEXT DEFAULT 'Toshkent',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                message TEXT,
                message_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                message TEXT,
                status TEXT DEFAULT 'pending',
                admin_reply TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                replied_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                day_number INTEGER,
                task_id TEXT,
                completed BOOLEAN DEFAULT 0,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, day_number, task_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                day_number INTEGER,
                task_id TEXT,
                title TEXT,
                description TEXT,
                time TEXT,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                day_number INTEGER,
                progress_percentage INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, day_number)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zikr_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                day_number INTEGER,
                zikr_id TEXT,
                count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, day_number, zikr_id)
            )
        ''')

        # Foydalanuvchi harakatlari logi — qachon nima qilgani
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                first_name TEXT,
                username TEXT,
                action TEXT,
                detail TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")

    def add_user(self, user_id, username, first_name, last_name, city='Toshkent'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, city, last_active)
            VALUES (?, ?, ?, ?, ?, datetime('now', '+5 hours'))
        ''', (user_id, username, first_name, last_name, city))
        cursor.execute('''
            UPDATE users SET last_active = datetime('now', '+5 hours') WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()

    def set_user_city(self, user_id, city):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET city = ? WHERE user_id = ?', (city, user_id))
        conn.commit()
        conn.close()

    def get_user_city(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT city FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 'Toshkent'

    def save_user_message(self, user_id, username, first_name, message, message_type='general'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_messages (user_id, username, first_name, message, message_type, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now', '+5 hours'))
        ''', (user_id, username, first_name, message, message_type))
        conn.commit()
        conn.close()

    def save_admin_request(self, user_id, username, first_name, message):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO admin_requests (user_id, username, first_name, message, created_at)
            VALUES (?, ?, ?, ?, datetime('now', '+5 hours'))
        ''', (user_id, username, first_name, message))
        conn.commit()
        conn.close()

    def get_pending_requests(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, username, first_name, message, created_at
            FROM admin_requests WHERE status = 'pending'
            ORDER BY created_at DESC LIMIT 10
        ''')
        results = cursor.fetchall()
        conn.close()
        return results

    def save_feedback(self, user_id, username, first_name, message):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO feedback (user_id, username, first_name, message, created_at)
            VALUES (?, ?, ?, ?, datetime('now', '+5 hours'))
        ''', (user_id, username, first_name, message))
        conn.commit()
        conn.close()
    

    # ================== TASK METODLARI ==================

    def save_task_completion(self, user_id: int, day_number: int, task_id: str, completed: bool):
        """Web App dan kelgan galochkani saqlash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if completed:
                cursor.execute('''
                    INSERT INTO daily_tasks (user_id, day_number, task_id, completed, completed_at)
                    VALUES (?, ?, ?, 1, datetime('now', '+5 hours'))
                    ON CONFLICT(user_id, day_number, task_id)
                    DO UPDATE SET completed = 1, completed_at = datetime('now', '+5 hours')
                ''', (user_id, day_number, task_id))
            else:
                cursor.execute('''
                    INSERT INTO daily_tasks (user_id, day_number, task_id, completed)
                    VALUES (?, ?, ?, 0)
                    ON CONFLICT(user_id, day_number, task_id)
                    DO UPDATE SET completed = 0, completed_at = NULL
                ''', (user_id, day_number, task_id))
            conn.commit()
            logger.info(f"✅ Task saved: user={user_id}, day={day_number}, task={task_id}, completed={completed}")
            return True
        except Exception as e:
            logger.error(f"Task save error: {e}")
            return False
        finally:
            conn.close()

    def get_user_tasks(self, user_id: int, day_number: int) -> dict:
        """Foydalanuvchining ma'lum kun vazifalarini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT task_id, completed, completed_at
            FROM daily_tasks
            WHERE user_id = ? AND day_number = ?
        ''', (user_id, day_number))
        rows = cursor.fetchall()
        conn.close()

        tasks = {}
        for row in rows:
            tasks[row[0]] = {
                "completed": bool(row[1]),
                "completed_at": row[2]
            }
        return tasks

    def save_bulk_tasks(self, user_id: int, day_number: int, tasks: list):
        """Web App dan kelgan barcha vazifalarni bir vaqtda saqlash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            for task in tasks:
                task_id = task.get('id') or task.get('task_id')
                completed = bool(task.get('completed', False))
                if completed:
                    cursor.execute('''
                        INSERT INTO daily_tasks (user_id, day_number, task_id, completed, completed_at)
                        VALUES (?, ?, ?, 1, datetime('now', '+5 hours'))
                        ON CONFLICT(user_id, day_number, task_id)
                        DO UPDATE SET completed = 1, completed_at = datetime('now', '+5 hours')
                    ''', (user_id, day_number, task_id))
                else:
                    cursor.execute('''
                        INSERT INTO daily_tasks (user_id, day_number, task_id, completed)
                        VALUES (?, ?, ?, 0)
                        ON CONFLICT(user_id, day_number, task_id)
                        DO UPDATE SET completed = 0, completed_at = NULL
                    ''', (user_id, day_number, task_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Bulk task save error: {e}")
            return False
        finally:
            conn.close()

    def update_daily_progress(self, user_id: int, day_number: int, progress: int):
        """Kunlik progressni yangilash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO daily_progress (user_id, day_number, progress_percentage, updated_at)
                VALUES (?, ?, ?, datetime('now', '+5 hours'))
                ON CONFLICT(user_id, day_number)
                DO UPDATE SET progress_percentage = ?, updated_at = datetime('now', '+5 hours')
            ''', (user_id, day_number, progress, progress))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Progress update error: {e}")
            return False
        finally:
            conn.close()

    def save_zikr_count(self, user_id: int, day_number: int, zikr_id: str, count: int):
        """Zikr sanini saqlash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO zikr_progress (user_id, day_number, zikr_id, count)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, day_number, zikr_id)
                DO UPDATE SET count = ?
            ''', (user_id, day_number, zikr_id, count, count))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Zikr save error: {e}")
            return False
        finally:
            conn.close()

    def get_zikr_counts(self, user_id: int, day_number: int) -> dict:
        """Foydalanuvchining zikr sanlarini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT zikr_id, count FROM zikr_progress
            WHERE user_id = ? AND day_number = ?
        ''', (user_id, day_number))
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}

    def get_user_stats(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM daily_tasks WHERE user_id = ? AND completed = 1
        ''', (user_id,))
        total_completed = cursor.fetchone()[0]

        cursor.execute('''
            SELECT COUNT(*) FROM daily_progress
            WHERE user_id = ? AND progress_percentage >= 70
        ''', (user_id,))
        completed_days = cursor.fetchone()[0]

        cursor.execute('''
            SELECT AVG(progress_percentage) FROM daily_progress WHERE user_id = ?
        ''', (user_id,))
        avg_progress = cursor.fetchone()[0] or 0

        cursor.execute('''
            SELECT day_number, progress_percentage FROM daily_progress
            WHERE user_id = ? ORDER BY day_number DESC
        ''', (user_id,))
        streak = 0
        for row in cursor.fetchall():
            if row[1] >= 70:
                streak += 1
            else:
                break

        conn.close()
        return {
            'total_completed': total_completed,
            'completed_days': completed_days,
            'avg_progress': round(avg_progress, 1),
            'current_streak': streak
        }

    def get_all_users_with_city(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, city FROM users')
        results = cursor.fetchall()
        conn.close()
        return results

    def get_total_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_active_users_today(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM users WHERE DATE(last_active) = DATE(datetime('now', '+5 hours'))
        ''')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def log_activity(self, user_id: int, first_name: str, username: str, action: str, detail: str = ""):
        """Foydalanuvchi harakatini loglaydi"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO user_activity_log (user_id, first_name, username, action, detail, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now', '+5 hours'))
            ''', (user_id, first_name, username or "", action, detail))
            conn.commit()
        except Exception as e:
            logger.error(f"Log activity error: {e}")
        finally:
            conn.close()

    def get_user_activity(self, user_id: int, limit: int = 20):
        """Bitta foydalanuvchining so'nggi harakatlarini qaytaradi"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT action, detail, created_at FROM user_activity_log
            WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_all_users_detailed(self):
        """Barcha foydalanuvchilar — batafsil ma'lumot"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.user_id, u.first_name, u.username, u.city, u.created_at, u.last_active,
                   COUNT(DISTINCT dt.day_number) as active_days,
                   SUM(CASE WHEN dt.completed=1 THEN 1 ELSE 0 END) as completed_tasks
            FROM users u
            LEFT JOIN daily_tasks dt ON u.user_id = dt.user_id
            GROUP BY u.user_id
            ORDER BY u.last_active DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_today_active_users(self):
        """Bugun faol bo'lgan foydalanuvchilar ro'yxati"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT u.user_id, u.first_name, u.username, u.city,
                   COUNT(DISTINCT al.action) as actions_count,
                   MAX(al.created_at) as last_action
            FROM users u
            LEFT JOIN user_activity_log al ON u.user_id = al.user_id
                AND DATE(al.created_at) = DATE(datetime('now', '+5 hours'))
            WHERE DATE(u.last_active) = DATE(datetime('now', '+5 hours'))
            GROUP BY u.user_id
            ORDER BY last_action DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows


db = Database()


# ================== KEYBOARD ==================
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("📱 Dasturni Ochish", web_app=WebAppInfo(url=WEB_APP_URL))],
        [KeyboardButton("📊 Statistika"), KeyboardButton("💬 Fikr Qoldirish")],
        [KeyboardButton("Saharlik duosi"), KeyboardButton("Iftorlik duosi"),
         KeyboardButton("👨‍💼 Admin bilan Bog'lanish"), KeyboardButton("ℹ️ Yordam")],
        [KeyboardButton("📅 1 Oylik Taqvim")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_city_keyboard():
    keyboard = [
        [KeyboardButton("🏙️ Toshkent")],
        [KeyboardButton("🏙️ Urganch")],
        [KeyboardButton("🏙️ Shovot")],
        [KeyboardButton("🔙 Orqaga")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ramadan_day = get_ramadan_day()

    if ramadan_day == 0:
        days_until = (RAMADAN_START_DATE - date.today()).days
        await update.message.reply_text(
            f"🌙 *Ramazon oyiga {days_until} kun qoldi!*\n\n"
            f"Ramazon {RAMADAN_START_DATE.strftime('%d %B %Y')} da boshlanadi.\n\n"
            f"_Bot o'sha kundan ishlay boshlaydi._",
            parse_mode='Markdown'
        )
        return

    if ramadan_day == -1:
        await update.message.reply_text(
            "🌙 *Ramazon oyi tugadi!*\n\n_Hayit muborak bo'lsin!_",
            parse_mode='Markdown'
        )
        return

    db.add_user(user.id, user.username, user.first_name, user.last_name)
    db.log_activity(user.id, user.first_name, user.username, "BOT_OCHDI", "/start buyrug'i")

    welcome_text = f"""
🌙 *Assalomu alaykum, {user.first_name}!*

*Ramazon oyi muborak bo'lsin!* 🤲

📅 *Bugun Ramazonning {ramadan_day}-kuni*
📆 {get_ramadan_date_for_day(ramadan_day).strftime('%d %B %Y')}

Ramazon dasturi botiga xush kelibsiz!

_Shaharingizni tanlang..._
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

    city_text = "🏙️ *Shaharingizni tanlang*\n\nSaharlik va iftor vaqtlari shaharingizga qarab belgilanadi."
    await update.message.reply_text(
        city_text,
        parse_mode='Markdown',
        reply_markup=get_city_keyboard()
    )


# ================== SHAHAR TANLASH ==================
async def select_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    ramadan_day = get_ramadan_day()

    if text == "🔙 Orqaga":
        await show_main_menu(update, context)
        return

    city = text.replace("🏙️ ", "")
    if city in CITY_TIMES:
        db.set_user_city(user.id, city)

        try:
            if INTRO_VIDEO_ID:
                caption = f"🎥 *Ramazon oyi haqida qisqacha*\n"
                await update.message.reply_video(video=INTRO_VIDEO_ID, caption=caption, parse_mode='Markdown')
        except:
            pass

        info_text = f"""
✅ *{city} shahri tanlandi!*

📅 *Bugun Ramazonning {ramadan_day}-kuni*

📚 *30 kun ichida o'zingizni qaytadan kashf qiling:*

✅ Kunlik vazifalar 
✅ Zikr tracker 
✅ 99 ism - Allohning go'zal ismlari
✅ Jannat Bog'i 🌿
✅ Batafsil statistikangiz
✅ Vaqt eslatmalari 
✅ Sizga har kuni yangi videolar


*Eslatmalar:*
🌅 Saharlik: 10 minut oldin
🌆 Iftor: 15 va 5 minut oldin

"""
        await update.message.reply_text(info_text, parse_mode='Markdown')

        try:
            if RAMADAN_VIDEO_ID:
                caption = f"🌙 *Ramazon - O'zgarish Oyi*\n\n📅 {ramadan_day}/30 kun"
                await update.message.reply_video(video=RAMADAN_VIDEO_ID, caption=caption, parse_mode='Markdown')
        except:
            pass

        await show_main_menu(update, context)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ramadan_day = get_ramadan_day()
    final_text = f"""
🎯 *Tayyor bo'lsangiz, boshlaylik!*

📅 *Bugun Ramazonning {ramadan_day}-kuni*

Quyidagi tugmalardan tanlang:

📱 *Dasturni Ochish* - Vazifalar
📊 *Statistika* - Natijalar  
💬 *Fikr Qoldirish* - Takliflar
👨‍💼 *Admin* - Yordam
ℹ️ *Yordam* - Yo'riqnoma
📅 *Taqvim* - 30 kunlik

_Alloh qilayotgan yaxshi amallaringizni qabul qilsin!_ 🤲
"""
    await update.message.reply_text(final_text, parse_mode='Markdown', reply_markup=get_main_keyboard())


# ================== SAHARLIK DUOSI ==================
async def show_saharlik_duosi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ramadan_day = get_ramadan_day()
    city = db.get_user_city(user_id)

    # Bugungi vaqtlarni olish
    times_list = CITY_TIMES.get(city, TOSHKENT_TIMES)
    if 1 <= ramadan_day <= 30:
        today_times = times_list[ramadan_day - 1]
        time_info = f"\n🌅 *Saharlik vaqti ({city}):* `{today_times['saharlik']}`\n"
    else:
        time_info = ""

    text = f"""
🌅 *Saharlik vaqti*

📅 Ramazonning {ramadan_day}-kuni{time_info}
{SAHARLIK_DUOSI}

━━━━━━━━━━━━━━━━━━━━
💡 *Eslatma:* Saharlik qilish sunnat bo'lib, kechiktirmasdan og'iz yopish afzaldir.

_Alloh qabul qilsin!_ 🤲
"""
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=get_main_keyboard())


# ================== IFTORLIK DUOSI ==================
async def show_iftor_duosi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ramadan_day = get_ramadan_day()
    city = db.get_user_city(user_id)

    times_list = CITY_TIMES.get(city, TOSHKENT_TIMES)
    if 1 <= ramadan_day <= 30:
        today_times = times_list[ramadan_day - 1]
        time_info = f"\n🌆 *Iftor vaqti ({city}):* `{today_times['iftor']}`\n"
    else:
        time_info = ""

    text = f"""
🌆 *Iftor vaqti*

📅 Ramazonning {ramadan_day}-kuni{time_info}
{IFTOR_DUOSI}

━━━━━━━━━━━━━━━━━━━━
💡 *Eslatma:* Iftor vaqti kirganda imkon qadar tezda og'iz ochish mustahab hisoblanadi. Xurmo yoki suv bilan iftor qilish sunnatdir.

🤲 *Iftor paytida qabul bo'ladigan duolar:*
• Ro'zador kishi iftorida
• Safar qilayotgan shaxsning duosi  
• Mazlumning duosi

_Tutgan ro'zangiz qabul bo'lsin!_ 🤲
"""
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=get_main_keyboard())


# ================== TAQVIM ==================
async def show_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📅 *1 Oylik Taqvim*\n\nShaharingizni tanlang:"
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=get_city_keyboard())
    context.user_data['selecting_calendar_city'] = True


async def send_calendar_image(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    ramadan_day = get_ramadan_day()

    if city in CALENDAR_IMAGES:
        try:
            caption = f"""
📅 *{city} - 30 Kunlik Taqvim*

📆 Bugun: Ramazonning {ramadan_day}-kuni
📆 Sana: {get_ramadan_date_for_day(ramadan_day).strftime('%d %B %Y')}

_Ramazon: 19 Fevral - 20 Mart 2026_
"""
            await update.message.reply_photo(
                photo=CALENDAR_IMAGES[city],
                caption=caption,
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )
        except Exception as e:
            logger.error(f"Calendar image error: {e}")
            await _send_text_calendar(update, city, ramadan_day)
    else:
        await _send_text_calendar(update, city, ramadan_day)


async def _send_text_calendar(update: Update, city: str, ramadan_day: int):
    times = CITY_TIMES[city]
    calendar_text = f"📅 *{city} - 30 Kunlik Taqvim*\n\n"
    for i, t in enumerate(times, 1):
        mark = "✅" if i < ramadan_day else "📍" if i == ramadan_day else "⏳"
        calendar_text += f"{mark} {i}-kun: 🌅 {t['saharlik']} | 🌆 {t['iftor']}\n"
    await update.message.reply_text(calendar_text, parse_mode='Markdown', reply_markup=get_main_keyboard())


# ================== STATISTIKA ==================
async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ramadan_day = get_ramadan_day()
    stats = db.get_user_stats(user_id)

    # Bugungi vazifalarni olish
    today_tasks = db.get_user_tasks(user_id, ramadan_day)
    today_completed = sum(1 for t in today_tasks.values() if t['completed'])

    stats_text = f"""
📊 *Sizning Statistikangiz*

📅 *Bugun: Ramazonning {ramadan_day}-kuni*

📋 *Bugungi vazifalar:* {today_completed} ta bajarildi

━━━━━━━━━━━━━━━━━━━━
✅ *Jami bajarilgan vazifalar:* {stats['total_completed']}
🌟 *To'liq kunlar (70%+):* {stats['completed_days']}
📈 *O'rtacha progress:* {stats['avg_progress']}%
🔥 *Hozirgi streak:* {stats['current_streak']} kun

_{stats['completed_days']}/30 kun to'liq bajarildi!_

Davom eting! 💪
"""
    await update.message.reply_text(stats_text, parse_mode='Markdown', reply_markup=get_main_keyboard())


# ================== FIKR-MULOHAZA ==================
async def request_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ramadan_day = get_ramadan_day()
    text = f"""
💬 *Fikr-mulohaza*

📅 Bugun: Ramazonning {ramadan_day}-kuni

Botni yaxshilash uchun takliflaringiz(men uchun muhim):

_Xabaringizni yozing:_
"""
    await update.message.reply_text(text, parse_mode='Markdown')
    context.user_data['awaiting_feedback'] = True


async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_feedback'):
        user = update.effective_user
        message = update.message.text
        ramadan_day = get_ramadan_day()

        db.save_feedback(user.id, user.username, user.first_name, message)
        db.save_user_message(user.id, user.username, user.first_name, message, 'feedback')

        await update.message.reply_text(
            f"✅ *Rahmat!* Fikringiz qabul qilindi.\n\n📅 Ramazonning {ramadan_day}-kuni",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )

        try:
            admin_text = f"""
📩 *Yangi Fikr-mulohaza!*

📅 Ramazonning {ramadan_day}-kuni

👤 *User:* {user.first_name}
🆔 *Username:* @{user.username or 'Yoq'}
💬 *Xabar:*

{message}

_Vaqt: {datetime.now(TASHKENT_TZ).strftime('%Y-%m-%d %H:%M:%S')}_
"""
            await context.bot.send_message(ADMIN_ID, admin_text, parse_mode='Markdown')
        except:
            pass

        context.user_data['awaiting_feedback'] = False


# ================== ADMIN MUROJAT ==================
async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ramadan_day = get_ramadan_day()
    text = f"""
👨‍💼 *Admin bilan bog'lanish*

📅 Bugun: Ramazonning {ramadan_day}-kuni

_Xabaringizni kiriting:_
"""
    await update.message.reply_text(text, parse_mode='Markdown')
    context.user_data['awaiting_admin_message'] = True


async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_admin_message'):
        user = update.effective_user
        message = update.message.text
        ramadan_day = get_ramadan_day()

        db.save_admin_request(user.id, user.username, user.first_name, message)
        db.save_user_message(user.id, user.username, user.first_name, message, 'admin_request')

        await update.message.reply_text(
            f"✅ *Xabar yuborildi!*\n\n📅 Ramazonning {ramadan_day}-kuni\n\nAdmin tez orada javob beradi.",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )

        try:
            keyboard = [[InlineKeyboardButton("💬 Javob berish", callback_data=f"reply_{user.id}")]]
            admin_text = f"""
📨 *Yangi Admin Murojat!*

📅 Ramazonning {ramadan_day}-kuni

👤 *User:* {user.first_name} {user.last_name or ''}
🆔 *Username:* @{user.username or 'Yoq'}
🔢 *User ID:* `{user.id}`

💬 *Xabar:*
{message}

_Vaqt: {datetime.now(TASHKENT_TZ).strftime('%Y-%m-%d %H:%M:%S')}_
"""
            await context.bot.send_message(
                ADMIN_ID, admin_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            print("ADMIN SEND ERROR:", e)

        context.user_data['awaiting_admin_message'] = False


# ================== YORDAM ==================
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ramadan_day = get_ramadan_day()
    help_text = f"""
ℹ️ *Yordam* 

📅 *Bugun: Ramazonning {ramadan_day}-kuni*

*1️⃣ Dasturni Oching*
📱 Sizga berilgan kunlik vazifalarni bajaring
📊 O'z intizomingizni kuzatib boring

*2️⃣ Duolar*
🤲 Saharlik duosi - tugmadan toping
🤲 Iftorlik duosi - tugmadan toping

*3️⃣ Vaqt Eslatmalari*
🌅 Saharlik: 10 minut oldin
🌆 Iftor: 15 va 5 minut oldin


_Savol bo'lsa - Admin bilan bog'laning!(admin panell orqali)_
"""
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=get_main_keyboard())


# ================== ADMIN PANEL ==================
async def admin_reply_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split('_')[1])
    await query.edit_message_text(
        f"✍️ Javobingizni yozing.\n_User ID: {user_id}_",
        parse_mode='Markdown'
    )
    context.user_data['admin_reply_to'] = user_id


async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID and context.user_data.get('admin_reply_to'):
        user_id = context.user_data['admin_reply_to']
        admin_message = update.message.text
        ramadan_day = get_ramadan_day()
        try:
            await context.bot.send_message(
                user_id,
                f"💬 *Admin javobi:*\n\n{admin_message}\n\n📅 Ramazonning {ramadan_day}-kuni",
                parse_mode='Markdown'
            )
            await update.message.reply_text("✅ Javob yuborildi!")
        except:
            await update.message.reply_text("❌ Xatolik!")
        context.user_data['admin_reply_to'] = None




async def admin_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/users — barcha foydalanuvchilar ro'yxati"""
    if update.effective_user.id != ADMIN_ID:
        return

    users = db.get_all_users_detailed()
    total = len(users)

    if not users:
        await update.message.reply_text("👥 Foydalanuvchilar yo'q")
        return

    # Sahifalash — har sahifada 10 ta
    page = int(context.args[0]) if context.args else 1
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    page_users = users[start:end]
    total_pages = (total + per_page - 1) // per_page

    text = f"👥 *Foydalanuvchilar ({total} ta) — {page}/{total_pages} sahifa*\n\n"

    for u in page_users:
        user_id, first_name, username, city, created_at, last_active, active_days, completed_tasks = u
        uname = f"@{username}" if username else "username yoq"
        last = last_active[:16] if last_active else "—"
        text += f"👤 *{first_name}* ({uname})\n"
        text += f"   🏙 {city} | 📅 {active_days} kun | ✅ {completed_tasks or 0} vazifa\n"
        text += f"   🕐 Oxirgi: {last}\n\n"

    if total_pages > 1:
        text += f"\n➡️ Keyingi sahifa: `/users {page + 1}`" if page < total_pages else ""

    await update.message.reply_text(text, parse_mode='Markdown')


async def admin_user_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/user 12345 — bitta foydalanuvchining batafsil ma'lumoti"""
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Foydalanish: `/user 12345`", parse_mode='Markdown')
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Noto'g'ri ID")
        return

    # Foydalanuvchi ma'lumoti
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, first_name, username, city, created_at, last_active FROM users WHERE user_id=?', (target_id,))
    user_row = cursor.fetchone()
    conn.close()

    if not user_row:
        await update.message.reply_text("❌ Foydalanuvchi topilmadi")
        return

    user_id, first_name, username, city, created_at, last_active = user_row
    stats = db.get_user_stats(user_id)
    activities = db.get_user_activity(user_id, 15)

    text = f"""
👤 *{first_name}*
🆔 ID: `{user_id}`
📛 Username: @{username or "yoq"}
🏙 Shahar: {city}
📅 Qo'shilgan: {created_at[:16] if created_at else "-"}
🕐 Oxirgi faollik: {last_active[:16] if last_active else "-"}

📊 *Statistika:*
✅ Jami vazifalar: {stats['total_completed']}
🌟 To'liq kunlar: {stats['completed_days']}
📈 O'rtacha: {stats['avg_progress']}%
🔥 Streak: {stats['current_streak']} kun

📋 *So'nggi harakatlar:*
"""
    for action, detail, created in activities[:10]:
        time_str = created[11:16] if created else "—"
        date_str = created[:10] if created else "—"
        text += f"• `{date_str} {time_str}` — {action}"
        if detail:
            text += f": _{detail[:40]}_"
        text += "\n"

    await update.message.reply_text(text, parse_mode='Markdown')




async def admin_get_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/getdb — bazani fayl sifatida yuboradi"""
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        import os
        db_path = 'ramadan_final.db'
        if not os.path.exists(db_path):
            await update.message.reply_text("❌ Baza topilmadi")
            return
        size = os.path.getsize(db_path)
        await update.message.reply_text(f"📦 Baza yuklanmoqda... ({size // 1024} KB)")
        with open(db_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename='ramadan_final.db',
                caption=f"🗄 Ramazon Bot Bazasi\n📅 {datetime.now(TASHKENT_TZ).strftime('%Y-%m-%d %H:%M')}\n📦 {size // 1024} KB"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")


async def admin_today_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/today — bugun faol bo'lgan foydalanuvchilar"""
    if update.effective_user.id != ADMIN_ID:
        return

    users = db.get_today_active_users()
    ramadan_day = get_ramadan_day()

    if not users:
        await update.message.reply_text(f"😔 Bugun hech kim kirmadi\n📅 Ramazonning {ramadan_day}-kuni")
        return

    text = f"📅 *Bugun faol ({len(users)} ta)*\n📅 Ramazonning {ramadan_day}-kuni\n\n"

    for u in users:
        user_id, first_name, username, city, actions_count, last_action = u
        uname = f"@{username}" if username else ""
        last = last_action[11:16] if last_action else "—"
        text += f"👤 {first_name} {uname} — 🏙{city} | {actions_count} harakat | 🕐{last}\n"

    await update.message.reply_text(text, parse_mode='Markdown')

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    total = db.get_total_users()
    active = db.get_active_users_today()
    ramadan_day = get_ramadan_day()
    text = f"""
📊 *Admin Panel*

📅 Ramazonning {ramadan_day}-kuni

👥 *Jami:* {total}
✅ *Bugun faol:* {active}
📈 *Faollik:* {round(active / total * 100 if total > 0 else 0, 1)}%
"""
    await update.message.reply_text(text, parse_mode='Markdown')


async def admin_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    requests = db.get_pending_requests()
    if not requests:
        await update.message.reply_text("📭 Yangi murojatlar yo'q")
        return
    for req in requests:
        req_id, user_id, username, first_name, message, created_at = req
        keyboard = [[InlineKeyboardButton("💬 Javob", callback_data=f"reply_{user_id}")]]
        text = f"📨 *Murojat #{req_id}*\n\n👤 {first_name}\n🆔 @{username or 'Yoq'}\n\n💬 {message}\n\n📅 {created_at}"
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))


# ================== WEB APP DATA HANDLER ==================
async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.web_app_data:
        user = update.effective_user
        raw_data = update.message.web_app_data.data

        logger.info(f"📲 Web App data received from {user.id}: {raw_data}")
        db.log_activity(user.id, user.first_name, user.username, "WEBAPP_OCHDI", "Web App ishlatdi")

        try:
            data = json.loads(raw_data)
            data_type = data.get("type", "")
            ramadan_day = get_ramadan_day()

            # ---- 1) Bitta vazifa yangilanishi ----
            if data_type == "task_update":
                day = data.get("day", ramadan_day)
                task_id = data.get("task_id")
                completed = bool(data.get("completed", False))
                if task_id:
                    db.save_task_completion(user.id, day, task_id, completed)
                    # XABAR YUBORISH O'CHIRILDI

            # ---- 2) Barcha vazifalar birdan (Tavsiya etilgan usul) ----
            elif data_type == "tasks_bulk":
                day = data.get("day", ramadan_day)
                tasks = data.get("tasks", [])
                progress = data.get("progress", 0)
                if tasks:
                    db.save_bulk_tasks(user.id, day, tasks)
                    db.update_daily_progress(user.id, day, progress)
                    # XABAR YUBORISH O'CHIRILDI

            # ---- 3) Zikr sani ----
            elif data_type == "zikr_update":
                day = data.get("day", ramadan_day)
                zikr_id = data.get("zikr_id")
                count = int(data.get("count", 0))
                if zikr_id:
                    db.save_zikr_count(user.id, day, zikr_id, count)
                    # XABAR YUBORISH O'CHIRILDI

            # ---- 4) Progress yangilanishi ----
            elif data_type == "progress_update":
                day = data.get("day", ramadan_day)
                progress = int(data.get("progress", 0))
                db.update_daily_progress(user.id, day, progress)

        except Exception as e:
            logger.error(f"Web app data error: {e}")



# ================== REST API SERVER (Web App uchun) ==================

def verify_telegram_user(init_data: str, bot_token: str):
    """Telegram initData dan user_id olish (tekshirish bilan)"""
    try:
        parsed = parse_qs(unquote(init_data))
        user_json = parsed.get('user', [None])[0]
        if user_json:
            user = json.loads(user_json)
            return user.get('id')
    except Exception as e:
        logger.error(f"initData parse error: {e}")
    return None


async def api_get_state(request: web.Request) -> web.Response:
    """GET /api/state?user_id=... - barcha kun ma'lumotlarini qaytaradi"""
    # CORS headerlar
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    try:
        # user_id olish
        user_id_str = request.rel_url.query.get('user_id', '')
        init_data = request.rel_url.query.get('init_data', '')
        
        user_id = None
        if init_data:
            user_id = verify_telegram_user(init_data, BOT_TOKEN)
        if not user_id and user_id_str.lstrip('-').isdigit():
            user_id = int(user_id_str)
        # demo_ prefiksli ID lar uchun (brauzerda test qilish)
        if not user_id and user_id_str.startswith('demo_'):
            user_id = user_id_str  # string sifatida saqlaymiz
        
        if not user_id:
            return web.json_response({'ok': False, 'error': 'Unauthorized'}, status=401, headers=headers)

        ramadan_day = get_ramadan_day()
        if ramadan_day <= 0:
            ramadan_day = 1

        all_days = []
        for day in range(1, 31):
            tasks = db.get_user_tasks(user_id, day)
            zikrs = db.get_zikr_counts(user_id, day)

            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT progress_percentage FROM daily_progress WHERE user_id=? AND day_number=?',
                (user_id, day)
            )
            row = cursor.fetchone()
            conn.close()
            progress = row[0] if row else 0

            # O'tgan kunlar lock qilinadi (faqat o'qish)
            is_locked = (day < ramadan_day)

            all_days.append({
                'day': day,
                'dailyTasks': {tid: info['completed'] for tid, info in tasks.items()},
                'zikr': zikrs,
                'progress': progress,
                'locked': is_locked
            })

        return web.json_response({
            'ok': True,
            'user_id': user_id,
            'current_day': ramadan_day,
            'days': all_days
        }, headers=headers)

    except Exception as e:
        logger.error(f"API get_state error: {e}")
        return web.json_response({'ok': False, 'error': str(e)}, status=500, headers=headers)


async def api_save_state(request: web.Request) -> web.Response:
    """POST /api/save - bugungi ma'lumotlarni saqlaydi"""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    # OPTIONS preflight
    if request.method == 'OPTIONS':
        return web.Response(status=204, headers=headers)
    try:
        body = await request.json()
        user_id_str = str(body.get('user_id', ''))
        init_data = body.get('init_data', '')

        user_id = None
        if init_data:
            user_id = verify_telegram_user(init_data, BOT_TOKEN)
        if not user_id and user_id_str.lstrip('-').isdigit():
            user_id = int(user_id_str)
        if not user_id and user_id_str.startswith('demo_'):
            user_id = user_id_str

        if not user_id:
            return web.json_response({'ok': False, 'error': 'Unauthorized'}, status=401, headers=headers)

        ramadan_day = get_ramadan_day()
        if ramadan_day <= 0:
            ramadan_day = 1
        
        day = int(body.get('day', ramadan_day))
        data_type = body.get('type', '')

        # Faqat bugungi kun uchun saqlash — o'tgan kunlar lock
        if day < ramadan_day:
            return web.json_response({
                'ok': False,
                'error': f"Kun {day} yakunlangan, o'zgartirib bo'lmaydi"
            }, status=403, headers=headers)

        if data_type == 'task_update':
            task_id = body.get('task_id')
            completed = bool(body.get('completed', False))
            if task_id:
                db.save_task_completion(user_id, day, task_id, completed)
                logger.info(f"API task_update: user={user_id}, day={day}, task={task_id}, done={completed}")

        elif data_type == 'tasks_bulk':
            tasks = body.get('tasks', [])
            progress = int(body.get('progress', 0))
            if tasks:
                db.save_bulk_tasks(user_id, day, tasks)
            db.update_daily_progress(user_id, day, progress)
            logger.info(f"API tasks_bulk: user={user_id}, day={day}, tasks={len(tasks)}, progress={progress}%")

        elif data_type == 'zikr_update':
            zikr_id = body.get('zikr_id')
            count = int(body.get('count', 0))
            if zikr_id:
                db.save_zikr_count(user_id, day, zikr_id, count)

        elif data_type == 'progress_update':
            progress = int(body.get('progress', 0))
            db.update_daily_progress(user_id, day, progress)

        return web.json_response({'ok': True}, headers=headers)

    except Exception as e:
        logger.error(f"API save_state error: {e}")
        return web.json_response({'ok': False, 'error': str(e)}, status=500, headers=headers)


async def api_options(request: web.Request) -> web.Response:
    """OPTIONS preflight uchun"""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    return web.Response(status=204, headers=headers)


async def start_api_server():
    """REST API server — polling bilan parallel ishlaydi"""
    import os
    # Railway da PORT bor, local da 8080
    port = int(os.environ.get('PORT', os.environ.get('API_PORT', 8080)))

    app = web.Application()
    app.router.add_get('/api/state', api_get_state)
    app.router.add_post('/api/save', api_save_state)
    app.router.add_route('OPTIONS', '/api/state', api_options)
    app.router.add_route('OPTIONS', '/api/save', api_options)
    app.router.add_get('/health', lambda r: web.json_response({'ok': True, 'status': 'running'}))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"✅ REST API server started on port {port}")


# ================== MATN HANDLER ==================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    db.save_user_message(user.id, user.username, user.first_name, text, 'general')
    db.log_activity(user.id, user.first_name, user.username, "XABAR", text[:100])

    if context.user_data.get('awaiting_feedback'):
        await handle_feedback(update, context)
        return

    if context.user_data.get('awaiting_admin_message'):
        await handle_admin_message(update, context)
        return

    if user.id == ADMIN_ID and context.user_data.get('admin_reply_to'):
        await handle_admin_reply(update, context)
        return

    # Admin oddiy matn yozsa — broadcast taklifi
    if user.id == ADMIN_ID and not context.user_data.get('awaiting_feedback') \
            and not context.user_data.get('awaiting_admin_message') \
            and not text.startswith("/"):
        # Tugmalar ro'yxati — broadcastga ketmasin
        known_buttons = [
            "📊 Statistika", "💬 Fikr Qoldirish", "👨‍💼 Admin bilan Bog'lanish",
            "ℹ️ Yordam", "📅 1 Oylik Taqvim", "Saharlik duosi", "Iftorlik duosi",
            "🔙 Orqaga", "🏙️ Toshkent", "🏙️ Urganch", "🏙️ Shovot"
        ]
        if text not in known_buttons and not text.startswith("🏙️"):
            users_count = db.get_total_users()
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(f"✅ Ha, {users_count} ta userlarga yuborish",
                                         callback_data=f"admin_text_confirm"),
                    InlineKeyboardButton("❌ Yo'q, bekor", callback_data="admin_text_cancel"),
                ]
            ])
            context.user_data['pending_text_broadcast'] = text
            await update.message.reply_text(
                f"📢 Bu matnni barcha userlarga yuborilaymi?\n\n"
                f"💬 *Matn:*\n{text[:200]}",
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            return

    # Taqvim uchun shahar tanlash
    if context.user_data.get('selecting_calendar_city'):
        if text.startswith("🏙️"):
            city = text.replace("🏙️ ", "")
            if city in CITY_TIMES:
                await send_calendar_image(update, context, city)
                context.user_data['selecting_calendar_city'] = False
                return
        elif text == "🔙 Orqaga":
            context.user_data['selecting_calendar_city'] = False
            await show_main_menu(update, context)
            return

    # Shahar tanlash (boshlang'ich)
    if text.startswith("🏙️"):
        await select_city(update, context)
        return

    # Tugmalar
    if text == "📊 Statistika":
        await show_statistics(update, context)
    elif text == "💬 Fikr Qoldirish":
        await request_feedback(update, context)
    elif text == "👨‍💼 Admin bilan Bog'lanish":
        await contact_admin(update, context)
    elif text == "ℹ️ Yordam":
        await show_help(update, context)
    elif text == "📅 1 Oylik Taqvim":
        await show_calendar(update, context)
    elif text == "Saharlik duosi":
        await show_saharlik_duosi(update, context)
    elif text == "Iftorlik duosi":
        await show_iftor_duosi(update, context)
    else:
        await update.message.reply_text(
            "🤔 Tushunmadim. Pastki paneldan tanlang.",
            reply_markup=get_main_keyboard()
        )


# ================== BROADCAST ==================

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Barcha userlarga xabar yuborish.
    Matn:  /broadcast Salom barchaga!
    Media: Video/rasmga reply qilib /broadcast yozing
    """
    if update.effective_user.id != ADMIN_ID:
        return

    users = db.get_all_users_with_city()
    total = len(users)
    replied = update.message.reply_to_message

    # Media (video/rasm/ovoz) yuborish
    if replied:
        success, failed = 0, 0
        status_msg = await update.message.reply_text(f"📤 Yuborilmoqda... 0/{total}")
        for i, (user_id, _) in enumerate(users):
            try:
                await replied.copy(chat_id=user_id)
                success += 1
            except:
                failed += 1
            if (i + 1) % 20 == 0:
                try:
                    await status_msg.edit_text(f"📤 Yuborilmoqda... {i + 1}/{total}")
                except:
                    pass
            await asyncio.sleep(0.05)
        await status_msg.edit_text(
            f"✅ *Broadcast tugadi!*\n\n✔️ Yuborildi: {success}\n❌ Xatolik: {failed}\n👥 Jami: {total}",
            parse_mode='Markdown'
        )
        return

    # Matn yuborish
    text_to_send = " ".join(context.args) if context.args else None
    if not text_to_send:
        await update.message.reply_text(
            "📢 *Broadcast ishlatish:*\n\n"
            "▶️ Matn: `/broadcast Salom!`\n"
            "▶️ Video/Rasm: Mediaga reply qilib `/broadcast`\n\n"
            "📅 Kunlik avtomatik: `/schedule 08:00 Matn`\n"
            "📋 Rejani ko'rish: `/schedule`\n"
            "🗑 Rejani o'chirish: `/schedule_clear`",
            parse_mode='Markdown'
        )
        return

    success, failed = 0, 0
    status_msg = await update.message.reply_text(f"📤 Yuborilmoqda... 0/{total}")
    for i, (user_id, _) in enumerate(users):
        try:
            await context.bot.send_message(user_id, text_to_send, parse_mode='Markdown')
            success += 1
        except:
            failed += 1
        if (i + 1) % 20 == 0:
            try:
                await status_msg.edit_text(f"📤 Yuborilmoqda... {i + 1}/{total}")
            except:
                pass
        await asyncio.sleep(0.05)
    await status_msg.edit_text(
        f"✅ *Broadcast tugadi!*\n\n✔️ Yuborildi: {success}\n❌ Xatolik: {failed}\n👥 Jami: {total}",
        parse_mode='Markdown'
    )


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Kunlik avtomatik xabar rejalashtirish.
    /schedule 08:00 Bugungi eslatma matni
    """
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args or len(context.args) < 2:
        scheduled = context.bot_data.get('scheduled_messages', [])
        if not scheduled:
            await update.message.reply_text(
                "📅 *Hozircha rejalashtirilgan xabar yo'q*\n\n"
                "Qo'shish: `/schedule 08:00 Matn`\n"
                "O'chirish: `/schedule_clear`\n\n"
                "💡 Har kuni shu vaqtda barcha userlarga yuboriladi.",
                parse_mode='Markdown'
            )
        else:
            text = "📅 *Rejalashtirilgan xabarlar:*\n\n"
            for i, s in enumerate(scheduled, 1):
                text += f"{i}. ⏰ `{s['time']}` — {s['text'][:60]}\n"
            await update.message.reply_text(text, parse_mode='Markdown')
        return

    time_str = context.args[0]
    message_text = " ".join(context.args[1:])

    try:
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        await update.message.reply_text("❌ Vaqt formati noto'g'ri!\nMisol: `/schedule 08:00 Matn`",
                                        parse_mode='Markdown')
        return

    if 'scheduled_messages' not in context.bot_data:
        context.bot_data['scheduled_messages'] = []

    context.bot_data['scheduled_messages'].append({'time': time_str, 'text': message_text})
    await update.message.reply_text(
        f"✅ *Rejalashtirildi!*\n\n⏰ Vaqt: `{time_str}`\n💬 Matn:\n{message_text}",
        parse_mode='Markdown'
    )


async def schedule_clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha rejalashtirilgan xabarlarni o'chirish"""
    if update.effective_user.id != ADMIN_ID:
        return
    context.bot_data['scheduled_messages'] = []
    await update.message.reply_text("🗑 Barcha rejalashtirilgan xabarlar o'chirildi.")


async def send_scheduled_messages(application):
    """Har daqiqa scheduled xabarlarni tekshiradi va yuboradi"""
    while True:
        try:
            current_time = datetime.now(TASHKENT_TZ).strftime("%H:%M")  # Toshkent vaqti
            scheduled = application.bot_data.get('scheduled_messages', [])
            today = str(date.today())

            for item in scheduled:
                if item.get('time') == current_time and item.get('sent_date') != today:
                    users = db.get_all_users_with_city()
                    sent = 0
                    for user_id, _ in users:
                        try:
                            await application.bot.send_message(user_id, item['text'], parse_mode='Markdown')
                            sent += 1
                        except:
                            pass
                        await asyncio.sleep(0.05)
                    item['sent_date'] = today
                    logger.info(f"📢 Scheduled '{item['time']}' — {sent} userlarga yuborildi")

            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Scheduled message error: {e}")
            await asyncio.sleep(60)


# ================== VAQT ESLATMALARI ==================
async def send_time_notifications(application):
    while True:
        try:
            now = datetime.now(TASHKENT_TZ)  # Toshkent vaqti UTC+5
            current_time = now.strftime("%H:%M")
            ramadan_day = get_ramadan_day()

            if ramadan_day <= 0 or ramadan_day > 30:
                await asyncio.sleep(3600)
                continue

            users = db.get_all_users_with_city()

            for user_id, city in users:
                times = CITY_TIMES.get(city, TOSHKENT_TIMES)[ramadan_day - 1]

                saharlik_time = datetime.strptime(times['saharlik'], "%H:%M")
                saharlik_reminder = (saharlik_time - timedelta(minutes=10)).strftime("%H:%M")

                if current_time == saharlik_reminder:
                    text = f"""
⏰ *Og'iz yopishga 10 minut qoldi!*

📅 *Ramazonning {ramadan_day}-kuni*
🌅 Saharlik vaqti: *{times['saharlik']}*

{SAHARLIK_DUOSI}

_Saharlik qilishga erinmang!_ 😊
"""
                    try:
                        await application.bot.send_message(user_id, text, parse_mode='Markdown')
                    except:
                        pass

                if current_time == times['saharlik']:
                    text = f"""
🌅 *Saharlik vaqti!*

📅 *Ramazonning {ramadan_day}-kuni*

Kuningiz xayrli o'tsin! 
Ro'zangizni to'liq tutishga harakat qiling.

_Alloh qabul qilsin!_ 🤲
"""
                    try:
                        await application.bot.send_message(user_id, text, parse_mode='Markdown')
                    except:
                        pass

                iftor_time = datetime.strptime(times['iftor'], "%H:%M")
                iftor_reminder_15 = (iftor_time - timedelta(minutes=15)).strftime("%H:%M")

                if current_time == iftor_reminder_15:
                    text = f"""
⏰ *Og'iz ochishga 15 minut qoldi!*

📅 *Ramazonning {ramadan_day}-kuni*
🌆 Iftor vaqti: *{times['iftor']}*

_Iftor vaqtida ko'proq duo qiling, ijobat bo'ladi!_ 🤲
"""
                    try:
                        await application.bot.send_message(user_id, text, parse_mode='Markdown')
                    except:
                        pass

                iftor_reminder_5 = (iftor_time - timedelta(minutes=5)).strftime("%H:%M")

                if current_time == iftor_reminder_5:
                    text = f"""
⏰ *Og'iz ochishga 5 minut qoldi!*

📅 *Ramazonning {ramadan_day}-kuni*
🌆 Iftor vaqti: *{times['iftor']}*

_Tutgan ro'zangiz qabul bo'lsin!_ 🤲

{IFTOR_DUOSI}
"""
                    try:
                        await application.bot.send_message(user_id, text, parse_mode='Markdown')
                    except:
                        pass

            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Notification error: {e}")
            await asyncio.sleep(60)


# ================== MAIN ==================
def main():
    import os
    application = Application.builder().token(BOT_TOKEN).build()

    if not ADMIN_ID :
        logger.warning("⚠️ Admin ID'ni kiriting!")

    async def admin_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Admin botga rasm/video/matn yuborganda:
        - Tasdiqlash tugmasi chiqadi
        - ✅ Yuborish bosilsa — barcha userlarga ketadi
        - ❌ Bekor qilish bossilsa — faqat file_id qaytaradi
        """
        user = update.effective_user
        if user.id != ADMIN_ID:
            return

        # file_id ni olish
        if update.message.video:
            file_id = update.message.video.file_id
            media_type = "🎥 Video"
        elif update.message.photo:
            file_id = update.message.photo[-1].file_id
            media_type = "📸 Rasm"
        elif update.message.document:
            file_id = update.message.document.file_id
            media_type = "📄 Fayl"
        else:
            return

        users_count = db.get_total_users()

        # Xabarni vaqtincha saqlash
        context.user_data['pending_broadcast_msg_id'] = update.message.message_id
        context.user_data['pending_broadcast_file_id'] = file_id
        context.user_data['pending_broadcast_type'] = media_type

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"✅ Ha, {users_count} ta userlarga yuborish",
                                     callback_data="admin_broadcast_confirm"),
                InlineKeyboardButton("❌ Yo'q, bekor", callback_data="admin_broadcast_cancel"),
            ]
        ])

        await update.message.reply_text(
            f"{media_type} qabul qilindi.\n\n"
            f"👥 *{users_count} ta* userlarga yuborilaymi?",
            parse_mode='Markdown',
            reply_markup=keyboard
        )

    async def admin_broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if update.effective_user.id != ADMIN_ID:
            return

        # ---- Media broadcast ----
        if query.data == "admin_broadcast_cancel":
            file_id = context.user_data.get('pending_broadcast_file_id', '')
            media_type = context.user_data.get('pending_broadcast_type', '')
            await query.edit_message_text(
                f"❌ Bekor qilindi.\n\n{media_type} FILE\\_ID:\n`{file_id}`",
                parse_mode='Markdown'
            )
            return

        if query.data == "admin_broadcast_confirm":
            msg_id = context.user_data.get('pending_broadcast_msg_id')
            if not msg_id:
                await query.edit_message_text("❌ Xabar topilmadi.")
                return

            users = db.get_all_users_with_city()
            total = len(users)
            await query.edit_message_text(f"📤 Yuborilmoqda... 0/{total}")

            success, failed = 0, 0
            for i, (user_id, _) in enumerate(users):
                try:
                    await context.bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=ADMIN_ID,
                        message_id=msg_id
                    )
                    success += 1
                except:
                    failed += 1

                if (i + 1) % 20 == 0:
                    try:
                        await query.edit_message_text(f"📤 Yuborilmoqda... {i + 1}/{total}")
                    except:
                        pass
                await asyncio.sleep(0.05)

            await query.edit_message_text(
                f"✅ *Broadcast tugadi!*\n\n"
                f"✔️ Yuborildi: {success}\n"
                f"❌ Xatolik: {failed}\n"
                f"👥 Jami: {total}",
                parse_mode='Markdown'
            )

        # ---- Matn broadcast ----
        if query.data == "admin_text_cancel":
            context.user_data.pop('pending_text_broadcast', None)
            await query.edit_message_text("❌ Bekor qilindi.")
            return

        if query.data == "admin_text_confirm":
            text_to_send = context.user_data.pop('pending_text_broadcast', None)
            if not text_to_send:
                await query.edit_message_text("❌ Matn topilmadi.")
                return

            users = db.get_all_users_with_city()
            total = len(users)
            await query.edit_message_text(f"📤 Yuborilmoqda... 0/{total}")

            success, failed = 0, 0
            for i, (user_id, _) in enumerate(users):
                try:
                    await context.bot.send_message(user_id, text_to_send, parse_mode='Markdown')
                    success += 1
                except:
                    failed += 1
                if (i + 1) % 20 == 0:
                    try:
                        await query.edit_message_text(f"📤 Yuborilmoqda... {i + 1}/{total}")
                    except:
                        pass
                await asyncio.sleep(0.05)

            await query.edit_message_text(
                f"✅ *Broadcast tugadi!*\n\n"
                f"✔️ Yuborildi: {success}\n"
                f"❌ Xatolik: {failed}\n"
                f"👥 Jami: {total}",
                parse_mode='Markdown'
            )

    application.add_handler(MessageHandler(
        filters.User(ADMIN_ID) & (filters.VIDEO | filters.PHOTO | filters.Document.ALL),
        admin_media_handler
    ))
    application.add_handler(CallbackQueryHandler(admin_broadcast_callback, pattern=r"^admin_broadcast_"))

    # ---- Handlers ----
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_stats))
    application.add_handler(CommandHandler("requests", admin_requests))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("schedule", schedule_command))
    application.add_handler(CommandHandler("getdb", admin_get_db))
    application.add_handler(CommandHandler("schedule_clear", schedule_clear_command))
    application.add_handler(CommandHandler("users", admin_users_list))
    application.add_handler(CommandHandler("user", admin_user_detail))
    application.add_handler(CommandHandler("today", admin_today_users))
    application.add_handler(CallbackQueryHandler(admin_reply_callback, pattern=r"^reply_\d+$"))

    # Web App data — eng muhim handler (birinchi)
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))

    # Matn handleri — oxirida
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Vaqt eslatmalari + Scheduled xabarlar
    application.job_queue.run_once(
        lambda context: asyncio.create_task(send_time_notifications(application)),
        when=0
    )
    application.job_queue.run_once(
        lambda context: asyncio.create_task(send_scheduled_messages(application)),
        when=1
    )

    ramadan_day = get_ramadan_day()
    logger.info("🤖 Bot ishga tushdi!")
    logger.info(f"📅 Ramazon kuni: {ramadan_day}")
    logger.info(f"📆 Boshlanish: {RAMADAN_START_DATE}")

    async def run_all():
        import os
        port = int(os.environ.get('PORT', os.environ.get('API_PORT', 8080)))

        # aiohttp REST API server
        app = web.Application()
        app.router.add_get('/api/state', api_get_state)
        app.router.add_post('/api/save', api_save_state)
        app.router.add_route('OPTIONS', '/api/state', api_options)
        app.router.add_route('OPTIONS', '/api/save', api_options)
        app.router.add_get('/health', lambda r: web.json_response({'ok': True, 'status': 'running'}))

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        logger.info(f"✅ REST API server port {port} da ishga tushdi")

        # Telegram bot polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("✅ Telegram bot polling boshlandi")

        # Faqat admin uchun buyruqlar ro'yxatini o'rnatamiz
        try:
            from telegram import BotCommand, BotCommandScopeChat
            admin_commands = [
                BotCommand("start",          "🔄 Botni qayta ishga tushirish"),
                BotCommand("admin",          "📊 Admin statistika"),
                BotCommand("users",          "👥 Barcha foydalanuvchilar"),
                BotCommand("today",          "📅 Bugun faol bo'lganlar"),
                BotCommand("user",           "🔍 User detail: /user 12345"),
                BotCommand("requests",       "📨 Murojatlar ro'yxati"),
                BotCommand("broadcast",      "📢 Xabar yuborish"),
                BotCommand("schedule",       "⏰ Jadval: /schedule 08:00 Matn"),
                BotCommand("getdb", "🗄 Bazani yuklab olish"),
                BotCommand("schedule_clear", "🗑 Jadvallarni o'chirish"),
            ]
            await application.bot.set_my_commands(
                admin_commands,
                scope=BotCommandScopeChat(chat_id=ADMIN_ID)
            )
            logger.info("✅ Admin buyruqlari o'rnatildi")
        except Exception as e:
            logger.error(f"Admin commands setup error: {e}")

        # Job queue
        application.job_queue.start()

        # Doim ishlaydi
        import signal
        stop_event = asyncio.Event()

        def handle_signal():
            stop_event.set()

        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, handle_signal)
            except Exception:
                pass

        await stop_event.wait()

        # To'xtatish
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        await runner.cleanup()

    asyncio.run(run_all())


if __name__ == '__main__':
    main()
