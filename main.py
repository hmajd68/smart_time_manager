# main.py
import flet as ft
from database.database import Database
from managers.task_manager import TaskManager
from managers.habit_manager import HabitManager
from managers.goal_manager import GoalManager
from managers.pomodoro_manager import PomodoroManager
from managers.gamification_manager import GamificationManager
from services.ai_service import AIService
from services.notification_service import NotificationService
from pages.dashboard import DashboardPage
from pages.tasks import TasksPage
from pages.calendar import CalendarPage
from pages.eisenhower import EisenhowerPage
from pages.pomodoro import PomodoroPage
from pages.habits import HabitsPage
from pages.goals import GoalsPage
from pages.focus import FocusPage
from pages.energy import EnergyPage
from pages.reports import ReportsPage
from pages.settings import SettingsPage

async def main(page: ft.Page):
    # تنظیمات اولیه
    page.title = "مدیر زمان هوشمند"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 10
    page.rtl = True
    page.bgcolor = ft.Colors.GREY_50
    
    # راه‌اندازی دیتابیس
    db = Database()
    
    # راه‌اندازی مدیران
    task_manager = TaskManager(db)
    habit_manager = HabitManager(db)
    goal_manager = GoalManager(db)
    gamification = GamificationManager(db)
    pomodoro_manager = PomodoroManager(db)
    
    # راه‌اندازی سرویس‌ها
    ai_service = AIService(task_manager)
    notification_service = NotificationService(db.db_path)
    notification_service.start()
    
    # ایجاد صفحه‌ها
    pages_dict = {
        "خانه": DashboardPage(page, task_manager, gamification, habit_manager).content,
        "کارها": TasksPage(page, task_manager, gamification).content,
        "تقویم": CalendarPage(page, task_manager, habit_manager, goal_manager).content,  # ✅ ارسال همه مدیران
        "آیزنهاور": EisenhowerPage(page, task_manager).content,
        "پومودورو": PomodoroPage(page, pomodoro_manager, gamification).content,
        "عادت‌ها": HabitsPage(page, habit_manager, gamification).content,
        "اهداف": GoalsPage(page, goal_manager, gamification).content,
        "تمرکز": FocusPage(page, gamification).content,
        "انرژی": EnergyPage(page, db).content,
        "گزارش‌ها": ReportsPage(page, task_manager, gamification, habit_manager, pomodoro_manager).content,
        "تنظیمات": SettingsPage(page, db, gamification, task_manager, habit_manager, goal_manager).content,  # 
    }
    
    page_list = ["خانه", "کارها", "تقویم", "آیزنهاور", "پومودورو", "عادت‌ها", "اهداف", 
                 "تمرکز", "انرژی", "گزارش‌ها", "تنظیمات"]
    
    def change_page(e):
        page.controls.clear()
        page.add(nav_bar)
        label = page_list[e.control.selected_index]
        page.add(pages_dict[label])
        page.update()
    
    # ✅ نوار ناوبری با روش صحیح - استفاده از NavigationBar با destinations
    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon="HOME", label="خانه"),
            ft.NavigationBarDestination(icon="LIST", label="کارها"),
            ft.NavigationBarDestination(icon="CALENDAR_MONTH", label="تقویم"),
            ft.NavigationBarDestination(icon="GRID_VIEW", label="آیزنهاور"),
            ft.NavigationBarDestination(icon="TIMER", label="پومودورو"),
            ft.NavigationBarDestination(icon="REPEAT", label="عادت‌ها"),
            ft.NavigationBarDestination(icon="FLAG", label="اهداف"),
            ft.NavigationBarDestination(icon="FOCUS_MODE", label="تمرکز"),
            ft.NavigationBarDestination(icon="ENERGY_SAVINGS_LEAF", label="انرژی"),
            ft.NavigationBarDestination(icon="BAR_CHART", label="گزارش‌ها"),
            ft.NavigationBarDestination(icon="SETTINGS", label="تنظیمات"),
        ],
        selected_index=0,
        on_change=change_page,
        bgcolor=ft.Colors.WHITE,
        elevation=5
    )
    
    # نمایش صفحه اولیه
    page.add(nav_bar)
    page.add(pages_dict["خانه"])
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
