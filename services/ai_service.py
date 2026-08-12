# services/ai_service.py
from managers.task_manager import TaskManager
from datetime import datetime, timedelta
import random

class AIService:
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self.energy_mapping = {
            "زیاد": {"time": 60, "type": "سخت"},
            "متوسط": {"time": 45, "type": "معمولی"},
            "کم": {"time": 30, "type": "سبک"}
        }
    
    def get_daily_plan(self, energy_level: str = "متوسط") -> dict:
        """تولید برنامه روزانه بر اساس انرژی"""
        tasks = self.task_manager.get_today_tasks()
        if not tasks:
            return {
                'message': "امروز هیچ کاری ندارید! 😊\nاز این فرصت برای استراحت یا کارهای شخصی استفاده کنید.",
                'priority_tasks': [],
                'overdue': [],
                'suggested_time': [],
                'suggestions': ["استراحت کن و انرژی بگیر!"],
                'focus_tips': "امروز روز خوبی برای برنامه‌ریزی آینده است."
            }
        
        # مرتب‌سازی بر اساس اولویت و انرژی
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                t.priority == "بالا",
                t.energy_level == energy_level,
                t.estimated_time or 30
            ),
            reverse=True
        )
        
        # تشخیص کارهای عقب‌افتاده
        today = datetime.now().date()
        overdue = []
        for task in tasks:
            if task.deadline:
                try:
                    deadline = datetime.strptime(task.deadline, "%Y-%m-%d").date()
                    if deadline < today:
                        overdue.append(task)
                except:
                    pass
        
        # الگوریتم ساده زمان‌بندی
        scheduled = []
        current_time = 8
        energy_info = self.energy_mapping.get(energy_level, self.energy_mapping["متوسط"])
        
        for task in sorted_tasks[:5]:
            duration = task.estimated_time or energy_info["time"]
            end_time = current_time + duration // 60
            scheduled.append({
                'task': task.title,
                'start': f"{current_time:02d}:00",
                'end': f"{end_time:02d}:00",
                'duration': duration,
                'priority': task.priority
            })
            current_time = end_time + 1
        
        # تولید پیشنهادات
        suggestions = []
        if overdue:
            suggestions.append(f"⚠️ {len(overdue)} کار عقب‌افتاده دارید!")
        
        if energy_level == "زیاد":
            suggestions.append("⚡ انرژی بالا! بهترین زمان برای کارهای سخت و چالش‌برانگیز است.")
        elif energy_level == "کم":
            suggestions.append("😴 انرژی پایین. کارهای ساده را اولویت بدهید.")
        else:
            suggestions.append("⚖️ تعادل را در کارهای مختلف رعایت کنید.")
        
        return {
            'message': self._generate_message(energy_level, len(tasks)),
            'priority_tasks': [t.title for t in sorted_tasks[:3]],
            'overdue': [t.title for t in overdue],
            'suggested_time': scheduled,
            'suggestions': suggestions,
            'focus_tips': self._get_focus_tip()
        }
    
    def _generate_message(self, energy_level: str, task_count: int) -> str:
        messages = {
            "زیاد": f"✨ انرژی شما امروز عالی است! {task_count} کار برای انجام دارید.",
            "متوسط": f"🌱 روز خوبی برای پیشرفت. {task_count} کار در برنامه دارید.",
            "کم": f"🪫 امروز انرژی کمتری دارید. روی {min(task_count, 3)} کار مهم تمرکز کنید."
        }
        return messages.get(energy_level, f"📋 {task_count} کار برای امروز دارید.")
    
    def _get_focus_tip(self) -> str:
        tips = [
            "🎯 تکنیک ۲۵/۵ (پومودورو) را امتحان کنید",
            "📱 گوشی را در حالت پرواز قرار دهید",
            "🍃 هر ۱ ساعت ۵ دقیقه پیاده‌روی کنید",
            "💪 با کارهای کوچک شروع کنید تا انگیزه بگیرید",
            "🧘 قبل از شروع کار، ۲ دقیقه نفس عمیق بکشید"
        ]
        return random.choice(tips)
    
    def analyze_wasted_time(self, completed_tasks: list) -> str:
        if not completed_tasks:
            return "هیچ کاری انجام نشده است. امروز رو با یه کار ساده شروع کن!"
        
        avg_time = sum(t.get('actual_time', 0) for t in completed_tasks) / len(completed_tasks)
        if avg_time > 60:
            return "⏰ زمان زیادی صرف کارها شده. تکنیک پومودورو رو امتحان کن!"
        elif avg_time < 15:
            return "⚡ کارها سریع انجام شدن! به همین شکل ادامه بده."
        else:
            return "🎯 سرعت مناسبی داری! برای بهتر شدن، کارهای مشابه رو با هم انجام بده."
