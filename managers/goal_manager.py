# managers/goal_manager.py
from database.database import Database
from database.models import Goal
from typing import List, Optional

class GoalManager:
    def __init__(self, db: Database):
        self.db = db
        self.goals: List[Goal] = []
        self.load()
    
    def load(self):
        rows = self.db.fetch_all('SELECT * FROM goals ORDER BY target_date')
        self.goals = []
        for row in rows:
            goal = Goal(
                id=row['id'],
                title=row['title'],
                description=row['description'] or "",
                goal_type=row['goal_type'] or "کوتاه‌مدت",
                target_date=row['target_date'],
                progress=row['progress'] or 0
            )
            # بارگذاری مراحل
            self.db.cursor.execute('SELECT * FROM goal_steps WHERE goal_id=?', (goal.id,))
            steps = self.db.cursor.fetchall()
            goal.steps = [step['title'] for step in steps]
            self.goals.append(goal)
    
    def add(self, title: str, description: str, goal_type: str, target_date: str) -> Goal:
        cursor = self.db.execute(
            'INSERT INTO goals (title, description, goal_type, target_date, progress) VALUES (?, ?, ?, ?, ?)',
            (title, description, goal_type, target_date, 0)
        )
        goal = Goal(
            id=cursor.lastrowid,
            title=title,
            description=description,
            goal_type=goal_type,
            target_date=target_date,
            progress=0,
            steps=[]
        )
        self.goals.append(goal)
        return goal
    
    def add_step(self, goal_id: int, step_title: str) -> bool:
        try:
            self.db.execute('INSERT INTO goal_steps (goal_id, title) VALUES (?, ?)', (goal_id, step_title))
            self.load()
            return True
        except:
            return False
    
    def update_progress(self, goal_id: int, progress: int) -> bool:
        try:
            self.db.execute('UPDATE goals SET progress=? WHERE id=?', (progress, goal_id))
            self.load()
            return True
        except:
            return False
    
    def delete(self, goal_id: int) -> bool:
        try:
            self.db.execute('DELETE FROM goals WHERE id=?', (goal_id,))
            self.db.execute('DELETE FROM goal_steps WHERE goal_id=?', (goal_id,))
            self.load()
            return True
        except:
            return False
    
    def get_all(self) -> List[Goal]:
        return self.goals
    
    def get_active(self) -> List[Goal]:
        return [g for g in self.goals if g.progress < 100]
    
    def get_completed(self) -> List[Goal]:
        return [g for g in self.goals if g.progress >= 100]