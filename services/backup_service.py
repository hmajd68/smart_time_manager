# services/backup_service.py
import os
import json
import shutil
import sqlite3
from datetime import datetime

class BackupService:
    def __init__(self, db_path="smart_time.db"):
        self.db_path = db_path
    
    def backup_with_json(self, backup_path=None):
        """پشتیبان‌گیری به صورت JSON"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_{timestamp}.json"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # دریافت تمام جداول
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            data = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                data[table_name] = [dict(zip(columns, row)) for row in rows]
            
            conn.close()
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return backup_path
        except Exception as e:
            print(f"خطا در پشتیبان‌گیری: {e}")
            return None
    
    def restore_from_json(self, json_path):
        """بازیابی از فایل JSON"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # حذف دیتابیس فعلی
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            
            # ایجاد دیتابیس جدید
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ایجاد جداول از داده‌ها
            for table_name, rows in data.items():
                if not rows:
                    continue
                
                # دریافت ستون‌ها
                columns = list(rows[0].keys())
                placeholders = ','.join(['?'] * len(columns))
                columns_str = ','.join(columns)
                
                for row in rows:
                    values = [row[col] for col in columns]
                    try:
                        cursor.execute(f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})", values)
                    except:
                        pass
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"خطا در بازیابی: {e}")
            return False
