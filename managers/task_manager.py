# managers/task_manager.py
from database.database import Database
from database.models import Task
from datetime import datetime, date
from typing import List, Optional
import jdatetime

class TaskManager:
    def __init__(self, db: Database):
        self.db = db
        self.tasks: List[Task] = []
        self.load()
    
    def load(self):
        rows = self.db.fetch_all('SELECT * FROM tasks ORDER BY done, priority DESC')
        self.tasks = [Task.from_row(row) for row in rows]
    
    def get_all(self) -> List[Task]:
        return self.tasks
    
    def get_today_tasks(self) -> List[Task]:
        today_str = date.today().strftime("%Y-%m-%d")
        return [t for t in self.tasks if not t.done and (t.deadline == today_str or (t.created_at and t.created_at.startswith(today_str)))]
    
    def get_by_category(self, category: str) -> List[Task]:
        return [t for t in self.tasks if t.category == category and not t.done]
    
    def get_by_priority(self, priority: str) -> List[Task]:
        return [t for t in self.tasks if t.priority == priority and not t.done]
    
    def get_by_eisenhower(self, eisenhower_type: str) -> List[Task]:
        return [t for t in self.tasks if t.eisenhower_type == eisenhower_type and not t.done]
    
    def get_by_date(self, date_str: str) -> List[Task]:
        """دریافت کارهای یک تاریخ مشخص (میلادی)"""
        return [t for t in self.tasks if t.deadline == date_str]
    
    def get_by_date_jalali(self, jalali_str: str) -> List[Task]:
        """دریافت کارهای یک تاریخ مشخص (شمسی)"""
        try:
            parts = jalali_str.split('/')
            if len(parts) == 3:
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                jalali_date = jdatetime.date(year, month, day)
                miladi = jalali_date.togregorian().strftime("%Y-%m-%d")
                return self.get_by_date(miladi)
        except:
            pass
        return []
    
    def get_upcoming_deadlines(self, days: int = 7) -> List[Task]:
        today = date.today()
        upcoming = []
        for task in self.tasks:
            if not task.done and task.deadline:
                try:
                    deadline = datetime.strptime(task.deadline, "%Y-%m-%d").date()
                    if 0 <= (deadline - today).days <= days:
                        upcoming.append(task)
                except:
                    continue
        return upcoming
    
    def add(self, task: Task) -> Task:
        task_dict = task.to_dict()
        query = '''
            INSERT INTO tasks 
            (title, description, category, priority, eisenhower_type, done, deadline, deadline_time, 
             created_at, estimated_time, actual_time, energy_level, reminder_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            task.title, task.description, task.category, task.priority, task.eisenhower_type,
            0, task.deadline, task.deadline_time, datetime.now().strftime("%Y-%m-%d %H:%M"),
            task.estimated_time, task.actual_time, task.energy_level, task.reminder_date, task.notes
        )
        cursor = self.db.execute(query, params)
        task.id = cursor.lastrowid
        self.load()
        return task
    
    def update(self, task: Task) -> bool:
        try:
            self.db.execute('''
                UPDATE tasks SET 
                    title=?, description=?, category=?, priority=?, eisenhower_type=?, 
                    done=?, deadline=?, deadline_time=?, estimated_time=?, actual_time=?,
                    energy_level=?, reminder_date=?, notes=?
                WHERE id=?
            ''', (
                task.title, task.description, task.category, task.priority, task.eisenhower_type,
                1 if task.done else 0, task.deadline, task.deadline_time,
                task.estimated_time, task.actual_time, task.energy_level, task.reminder_date, task.notes,
                task.id
            ))
            self.load()
            return True
        except:
            return False
    
    def delete(self, task_id: int) -> bool:
        try:
            self.db.execute('DELETE FROM tasks WHERE id=?', (task_id,))
            self.load()
            return True
        except:
            return False
    
    def toggle_done(self, task_id: int) -> bool:
        task = self.get_by_id(task_id)
        if task:
            task.done = not task.done
            return self.update(task)
        return False
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def search(self, query: str) -> List[Task]:
        return [t for t in self.tasks if query.lower() in t.title.lower() and not t.done]
    
    def get_stats(self) -> dict:
        total = len(self.tasks)
        done = len([t for t in self.tasks if t.done])
        categories = {}
        priorities = {}
        eisenhower = {}
        
        for task in self.tasks:
            if not task.done:
                categories[task.category] = categories.get(task.category, 0) + 1
                priorities[task.priority] = priorities.get(task.priority, 0) + 1
                eisenhower[task.eisenhower_type] = eisenhower.get(task.eisenhower_type, 0) + 1
        
        return {
            'total': total,
            'done': done,
            'pending': total - done,
            'completion_rate': (done / total * 100) if total > 0 else 0,
            'categories': categories,
            'priorities': priorities,
            'eisenhower': eisenhower
        }
