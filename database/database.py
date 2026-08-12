# database/database.py
import sqlite3
import os
import json
from datetime import datetime
import jdatetime

class Database:
    def __init__(self, db_path="smart_time.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"خطا در اتصال به دیتابیس: {e}")
            raise
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def execute(self, query, params=None):
        try:
            if params is None:
                params = []
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor
        except sqlite3.Error as e:
            print(f"خطا در اجرای کوئری: {e}")
            raise
    
    def fetch_all(self, query, params=None):
        self.execute(query, params)
        return self.cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        self.execute(query, params)
        return self.cursor.fetchone()
    
    def create_tables(self):
        # ===== جدول کارها =====
        self.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                priority TEXT,
                eisenhower_type TEXT,
                done INTEGER DEFAULT 0,
                deadline DATE,
                deadline_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estimated_time INTEGER,
                actual_time INTEGER,
                energy_level TEXT,
                reminder_date TIMESTAMP,
                notification_sent INTEGER DEFAULT 0,
                notes TEXT
            )
        ''')
        
        # ===== جدول عادت‌ها =====
        self.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                frequency TEXT,
                streak INTEGER DEFAULT 0,
                best_streak INTEGER DEFAULT 0,
                last_done DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ===== جدول ثبت عادت‌ها =====
        self.execute('''
            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER,
                log_date DATE,
                done INTEGER DEFAULT 0,
                FOREIGN KEY (habit_id) REFERENCES habits(id)
            )
        ''')
        
        # ===== جدول اهداف =====
        self.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                goal_type TEXT,
                target_date DATE,
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ===== جدول مراحل اهداف =====
        self.execute('''
            CREATE TABLE IF NOT EXISTS goal_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER,
                title TEXT,
                done INTEGER DEFAULT 0,
                FOREIGN KEY (goal_id) REFERENCES goals(id)
            )
        ''')
        
        # ===== جدول جلسات پومودورو =====
        self.execute('''
            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sessions INTEGER DEFAULT 0,
                total_time INTEGER DEFAULT 0
            )
        ''')
        
        # ===== جدول جلسات تمرکز =====
        self.execute('''
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration INTEGER,
                focus_type TEXT
            )
        ''')
        
        # ===== جدول انرژی روزانه =====
        self.execute('''
            CREATE TABLE IF NOT EXISTS daily_energy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                energy_level TEXT,
                mood TEXT,
                notes TEXT
            )
        ''')
        
        # ===== جدول گیمیفیکیشن =====
        self.execute('''
            CREATE TABLE IF NOT EXISTS gamification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                points INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                streak INTEGER DEFAULT 0,
                badges TEXT,
                total_focus_time INTEGER DEFAULT 0
            )
        ''')
        
        # ===== جدول تنظیمات =====
        self.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme TEXT DEFAULT 'light',
                language TEXT DEFAULT 'fa',
                pomodoro_work INTEGER DEFAULT 25,
                pomodoro_break INTEGER DEFAULT 5,
                pomodoro_long_break INTEGER DEFAULT 15,
                sound_enabled INTEGER DEFAULT 1,
                notifications_enabled INTEGER DEFAULT 1
            )
        ''')
        
        # ===== جدول یادآوری‌ها =====
        self.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                title TEXT,
                reminder_time TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        ''')
        
        # ===== ایندکس‌ها =====
        self.execute('CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks(deadline)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_habits_last_done ON habits(last_done)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_goals_target_date ON goals(target_date)')
        
        # ===== مقداردهی اولیه =====
        self.init_settings()
        self.init_gamification()
    
    def init_settings(self):
        result = self.fetch_one('SELECT * FROM settings')
        if not result:
            self.execute('''
                INSERT INTO settings 
                (theme, language, pomodoro_work, pomodoro_break, pomodoro_long_break, sound_enabled, notifications_enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('light', 'fa', 25, 5, 15, 1, 1))
    
    def init_gamification(self):
        result = self.fetch_one('SELECT * FROM gamification')
        if not result:
            self.execute('''
                INSERT INTO gamification (points, level, streak, badges, total_focus_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (0, 1, 0, json.dumps([]), 0))
