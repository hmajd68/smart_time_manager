# services/notification_service.py
import threading
import time
from datetime import datetime
import sqlite3

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
            print("✅ NotificationService started")
    
    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def register_callback(self, callback):
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def _run(self):
        while self.is_running:
            try:
                self.check_reminders()
                self.check_deadlines()
            except Exception as e:
                print(f"⚠️ Notification error: {e}")
            time.sleep(60)
    
    def check_reminders(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute('''
                SELECT r.*, t.title 
                FROM reminders r
                JOIN tasks t ON r.task_id = t.id
                WHERE r.reminder_time <= ? AND r.is_active = 1 AND t.done = 0
            ''', (now,))
            reminders = cursor.fetchall()
            for reminder in reminders:
                self.send_notification(f"⏰ یادآوری: {reminder[1]}")
                cursor.execute('UPDATE reminders SET is_active = 0 WHERE id = ?', (reminder[0],))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ check_reminders error: {e}")
    
    def check_deadlines(self):
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
                self.send_notification(f"⚠️ کار '{task[1]}' امروز ددلاین دارد!")
                cursor.execute('UPDATE tasks SET notification_sent = 1 WHERE id = ?', (task[0],))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ check_deadlines error: {e}")
    
    def send_notification(self, message):
        for callback in self.callbacks:
            try:
                callback(message)
            except:
                pass
        print(f"🔔 {message}")
