# managers/habit_manager.py
from database.database import Database
from database.models import Habit
from datetime import datetime, date
from typing import List, Optional

class HabitManager:
    def __init__(self, db: Database):
        self.db = db
        self.habits: List[Habit] = []
        self.load()
    
    def load(self):
        rows = self.db.fetch_all('SELECT * FROM habits ORDER BY created_at DESC')
        self.habits = []
        for row in rows:
            self.habits.append(Habit(
                id=row['id'],
                name=row['name'],
                frequency=row['frequency'] or "روزانه",
                streak=row['streak'] or 0,
                best_streak=row['best_streak'] or 0,
                last_done=row['last_done'],
                created_at=row['created_at']
            ))
    
    def add(self, name: str, frequency: str = "روزانه") -> Habit:
        today = date.today().strftime("%Y-%m-%d")
        cursor = self.db.execute(
            'INSERT INTO habits (name, frequency, last_done) VALUES (?, ?, ?)',
            (name, frequency, today)
        )
        habit = Habit(
            id=cursor.lastrowid,
            name=name,
            frequency=frequency,
            streak=0,
            best_streak=0,
            last_done=today,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        self.habits.append(habit)
        return habit
    
    def mark_done(self, habit_id: int) -> int:
        today = date.today().strftime("%Y-%m-%d")
        
        self.db.cursor.execute('SELECT last_done, streak, best_streak FROM habits WHERE id=?', (habit_id,))
        row = self.db.cursor.fetchone()
        
        if not row:
            return 0
        
        last_done = row[0]
        streak = row[1]
        best_streak = row[2]
        
        if last_done != today:
            try:
                last_date = datetime.strptime(last_done, "%Y-%m-%d").date()
                today_date = date.today()
                if (today_date - last_date).days == 1:
                    streak += 1
                else:
                    streak = 1
            except:
                streak = 1
            
            if streak > best_streak:
                best_streak = streak
            
            self.db.execute(
                'UPDATE habits SET last_done=?, streak=?, best_streak=? WHERE id=?',
                (today, streak, best_streak, habit_id)
            )
            
            # ثبت در جدول habit_logs
            self.db.execute(
                'INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)',
                (habit_id, today, 1)
            )
        
        self.load()
        return streak
    
    def delete(self, habit_id: int) -> bool:
        try:
            self.db.execute('DELETE FROM habits WHERE id=?', (habit_id,))
            self.db.execute('DELETE FROM habit_logs WHERE habit_id=?', (habit_id,))
            self.load()
            return True
        except:
            return False
    
    def get_all(self) -> List[Habit]:
        return self.habits
    
    def get_today_habits(self) -> List[Habit]:
        today = date.today().strftime("%Y-%m-%d")
        return [h for h in self.habits if h.last_done != today]
    
    def get_stats(self) -> dict:
        total = len(self.habits)
        done_today = len([h for h in self.habits if h.last_done == date.today().strftime("%Y-%m-%d")])
        total_streak = sum(h.streak for h in self.habits)
        best_streak = max(h.streak for h in self.habits) if self.habits else 0
        
        return {
            'total': total,
            'done_today': done_today,
            'total_streak': total_streak,
            'best_streak': best_streak,
            'completion_rate': (done_today / total * 100) if total > 0 else 0
        }