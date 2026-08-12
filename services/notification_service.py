# services/notification_service.py
import threading
import time
from datetime import datetime, timedelta
import sqlite3
import json

class NotificationService:
    def __init__(self, db_path="smart_time.db"):
        self.db_path = db_path
        self.is_running = False
        self.thread = None
        self.callbacks = []
    
    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
    
    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def register_callback(self, callback):
        """ثبت تابع برای نمایش اعلان"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def _run(self):
        while self.is_running:
            try:
                self.check_reminders()
                self.check_deadlines()
            except Exception as e:
                print(f"خطا در سرویس اعلان: {e}")
            time.sleep(60)  # هر ۱ دقیقه بررسی کن
    
    def check_reminders(self):
        """بررسی یادآوری‌ها"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute('''
                SELECT r.*, t.title, t.id as task_id 
                FROM reminders r
                JOIN tasks t ON r.task_id = t.id
                WHERE r.reminder_time <= ? AND r.is_active = 1 AND t.done = 0
            ''', (now,))
            
            reminders = cursor.fetchall()
            for reminder in reminders:
                # دسترسی با ایندکس
                title = reminder[1]  # ستون دوم title است
                self.send_notification(f"⏰ یادآوری: {title}")
                cursor.execute('UPDATE reminders SET is_active = 0 WHERE id = ?', (reminder[0],))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"خطا در بررسی یادآوری‌ها: {e}")
    
    def check_deadlines(self):
        """بررسی ددلاین‌های نزدیک"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute('''
                SELECT id, title, deadline FROM tasks 
                WHERE deadline <= ? AND done = 0 AND deadline IS NOT NULL AND notification_sent = 0
            ''', (today,))
            
            tasks = cursor.fetchall()
            for task in tasks:
                # دسترسی با ایندکس: id=0, title=1, deadline=2
                task_id = task[0]
                title = task[1]
                deadline = task[2]
                self.send_notification(f"⚠️ کار '{title}' امروز ددلاین دارد! ({deadline})")
                cursor.execute('UPDATE tasks SET notification_sent = 1 WHERE id = ?', (task_id,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"خطا در بررسی ددلاین‌ها: {e}")
    
    def send_notification(self, message):
        """ارسال اعلان به تمام callback‌های ثبت شده"""
        for callback in self.callbacks:
            try:
                callback(message)
            except:
                pass
        print(f"🔔 {message}")
    
    def add_reminder(self, task_id, reminder_time, title):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reminders (task_id, title, reminder_time, is_active)
                VALUES (?, ?, ?, ?)
            ''', (task_id, title, reminder_time, 1))
            conn.commit()
            conn.close()
            print(f"✅ یادآوری برای '{title}' ثبت شد")
        except Exception as e:
            print(f"خطا در ثبت یادآوری: {e}")
