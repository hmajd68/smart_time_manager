# database/database.py
import sqlite3
import os
import sys
import json
from datetime import datetime

class Database:
    def __init__(self, db_path="smart_time.db"):
        # اصلاح مسیر برای اندروید
        if hasattr(sys, '_MEIPASS'):
            self.db_path = os.path.join(os.path.dirname(sys.executable), db_path)
        else:
            self.db_path = db_path
            
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        try:
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            print(f"✅ دیتابیس متصل شد: {self.db_path}")
        except sqlite3.Error as e:
            print(f"❌ خطا در اتصال به دیتابیس: {e}")
            raise
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def execute(self, query, params=None):
        try:
            if params is None:
                params = []
            self.connect()
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor
        except sqlite3.Error as e:
            print(f"❌ خطا در اجرای کوئری: {e}")
            raise
    
    def fetch_all(self, query, params=None):
        self.execute(query, params)
        return self.cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        self.execute(query, params)
        return self.cursor.fetchone()
    
    def create_tables(self):
        # ... جداول قبلی ...
        pass
