# database/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import json
import jdatetime

@dataclass
class Task:
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    category: str = "سایر"
    priority: str = "متوسط"
    eisenhower_type: str = "مهم و غیر فوری"
    done: bool = False
    deadline: Optional[str] = None  # تاریخ میلادی
    deadline_time: Optional[str] = None
    created_at: Optional[str] = None
    estimated_time: int = 0
    actual_time: int = 0
    energy_level: str = "متوسط"
    reminder_date: Optional[str] = None
    notes: str = ""
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'eisenhower_type': self.eisenhower_type,
            'done': 1 if self.done else 0,
            'deadline': self.deadline,
            'deadline_time': self.deadline_time,
            'created_at': self.created_at,
            'estimated_time': self.estimated_time,
            'actual_time': self.actual_time,
            'energy_level': self.energy_level,
            'reminder_date': self.reminder_date,
            'notes': self.notes
        }
    
    def get_deadline_jalali(self):
        """دریافت تاریخ سررسید به شمسی"""
        if not self.deadline:
            return None
        try:
            miladi = datetime.strptime(self.deadline, "%Y-%m-%d")
            jalali = jdatetime.date.fromgregorian(date=miladi)
            return jalali.strftime("%Y/%m/%d")
        except:
            return self.deadline
    
    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row['id'],
            title=row['title'],
            description=row['description'] or "",
            category=row['category'] or "سایر",
            priority=row['priority'] or "متوسط",
            eisenhower_type=row['eisenhower_type'] or "مهم و غیر فوری",
            done=bool(row['done']),
            deadline=row['deadline'],
            deadline_time=row['deadline_time'],
            created_at=row['created_at'],
            estimated_time=row['estimated_time'] or 0,
            actual_time=row['actual_time'] or 0,
            energy_level=row['energy_level'] or "متوسط",
            reminder_date=row['reminder_date'],
            notes=row['notes'] or ""
        )

@dataclass
class Goal:
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    goal_type: str = "کوتاه‌مدت"
    target_date: Optional[str] = None  # تاریخ میلادی
    progress: int = 0
    steps: List[str] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
    
    def get_target_date_jalali(self):
        if not self.target_date:
            return None
        try:
            miladi = datetime.strptime(self.target_date, "%Y-%m-%d")
            jalali = jdatetime.date.fromgregorian(date=miladi)
            return jalali.strftime("%Y/%m/%d")
        except:
            return self.target_date

@dataclass
class Habit:
    id: Optional[int] = None
    name: str = ""
    frequency: str = "روزانه"
    streak: int = 0
    best_streak: int = 0
    last_done: Optional[str] = None  # تاریخ میلادی
    created_at: Optional[str] = None
    
    def get_last_done_jalali(self):
        if not self.last_done:
            return None
        try:
            miladi = datetime.strptime(self.last_done, "%Y-%m-%d")
            jalali = jdatetime.date.fromgregorian(date=miladi)
            return jalali.strftime("%Y/%m/%d")
        except:
            return self.last_done

@dataclass
class GamificationData:
    points: int = 0
    level: int = 1
    streak: int = 0
    badges: List[str] = None
    total_focus_time: int = 0
    
    def __post_init__(self):
        if self.badges is None:
            self.badges = []
    
    def to_json(self):
        return json.dumps(self.badges)
