# managers/gamification_manager.py
from database.database import Database
import json

class GamificationManager:
    def __init__(self, db: Database):
        self.db = db
        self.points = 0
        self.level = 1
        self.streak = 0
        self.badges = []
        self.total_focus_time = 0
        self.load()
    
    def load(self):
        self.db.cursor.execute('SELECT points, level, streak, badges, total_focus_time FROM gamification ORDER BY id DESC LIMIT 1')
        row = self.db.cursor.fetchone()
        if row:
            self.points = row[0]
            self.level = row[1]
            self.streak = row[2]
            self.badges = json.loads(row[3]) if row[3] else []
            self.total_focus_time = row[4]
        else:
            self.db.execute(
                'INSERT INTO gamification (points, level, streak, badges, total_focus_time) VALUES (0, 1, 0, "[]", 0)'
            )
    
    def save(self):
        self.db.execute(
            'UPDATE gamification SET points=?, level=?, streak=?, badges=?, total_focus_time=? WHERE id=1',
            (self.points, self.level, self.streak, json.dumps(self.badges), self.total_focus_time)
        )
    
    def add_points(self, points: int, reason: str = ""):
        self.points += points
        self.streak += 1
        old_level = self.level
        self.check_level_up()
        self.check_badges()
        self.save()
        return {
            'points': self.points,
            'level': self.level,
            'leveled_up': self.level > old_level,
            'reason': reason,
            'badges': self.badges
        }
    
    def add_focus_time(self, minutes: int):
        self.total_focus_time += minutes
        self.save()
        self.check_badges()
    
    def check_level_up(self):
        new_level = self.points // 100 + 1
        if new_level > self.level:
            self.level = new_level
            self.add_badge(f"سطح {self.level} 🏅")
    
    def check_badges(self):
        badges_config = [
            (50, "50 امتیاز ⭐"),
            (100, "100 امتیاز ⭐⭐"),
            (500, "500 امتیاز 🌟"),
            (7, "هفته اول 🎯"),
            (30, "ماه اول 🌟"),
            (60, "2 ماه اول 💪"),
            (100, "100 کار انجام شده 🎉"),
            (200, "200 کار انجام شده 🏆"),
        ]
        
        for threshold, badge in badges_config:
            if self.points >= threshold and badge not in self.badges:
                self.add_badge(badge)
        
        if self.total_focus_time >= 600:  # 10 ساعت
            self.add_badge("10 ساعت تمرکز 🧠")
        if self.total_focus_time >= 3600:  # 60 ساعت
            self.add_badge("60 ساعت تمرکز 🧠🧠")
        if self.total_focus_time >= 10000:  # 166 ساعت
            self.add_badge("10000 دقیقه تمرکز 💪")
    
    def add_badge(self, badge):
        if badge not in self.badges:
            self.badges.append(badge)
            self.save()
    
    def get_status(self):
        return {
            'points': self.points,
            'level': self.level,
            'streak': self.streak,
            'badges': self.badges,
            'total_focus_time': self.total_focus_time
        }
    
    def reset(self):
        self.points = 0
        self.level = 1
        self.streak = 0
        self.badges = []
        self.total_focus_time = 0
        self.save()