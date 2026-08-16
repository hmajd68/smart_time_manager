# main.py
import flet as ft
import traceback
import sys
import os
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
from pages.help import HelpPage

# ===== تنظیم مسیر دیتابیس برای اندروید =====
def get_db_path():
    """دریافت مسیر صحیح دیتابیس در اندروید"""
    if hasattr(sys, '_MEIPASS'):
        # اجرا در محیط打包 شده (اندروید)
        return os.path.join(os.path.dirname(sys.executable), 'smart_time.db')
    else:
        # اجرا در محیط توسعه
        return 'smart_time.db'

async def main(page: ft.Page):
    try:
        # تنظیمات اولیه
        page.title = "مدیر زمان هوشمند"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.scroll = ft.ScrollMode.AUTO
        page.padding = 10
        page.rtl = True
        page.bgcolor = ft.Colors.GREY_50
        
        # نمایش پیام Loading
        loading = ft.Text("⏳ در حال بارگذاری...", size=20, weight=ft.FontWeight.BOLD)
        page.add(loading)
        page.update()
        
        # راه‌اندازی دیتابیس با مسیر صحیح
        db = Database(get_db_path())
        
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
        
        # حذف پیام Loading
        page.controls.clear()
        
        # ایجاد صفحه‌ها
        pages_dict = {
            "خانه": DashboardPage(page, task_manager, gamification, habit_manager).content,
            "کارها": TasksPage(page, task_manager, gamification).content,
            "تقویم": CalendarPage(page, task_manager, habit_manager, goal_manager, db).content,
            "آیزنهاور": EisenhowerPage(page, task_manager).content,
            "پومودورو": PomodoroPage(page, pomodoro_manager, gamification).content,
            "عادت‌ها": HabitsPage(page, habit_manager, gamification).content,
            "اهداف": GoalsPage(page, goal_manager, gamification).content,
            "تمرکز": FocusPage(page, gamification).content,
            "انرژی": EnergyPage(page, db).content,
            "گزارش‌ها": ReportsPage(page, task_manager, gamification, habit_manager, pomodoro_manager).content,
            "تنظیمات": SettingsPage(page, db, gamification, task_manager, habit_manager, goal_manager).content,
            "راهنما": HelpPage(page).content,
        }
        
        page_list = ["خانه", "کارها", "تقویم", "آیزنهاور", "پومودورو", "عادت‌ها", "اهداف", 
                     "تمرکز", "انرژی", "گزارش‌ها", "تنظیمات", "راهنما"]
        
        def change_page(e):
            page.controls.clear()
            page.add(nav_bar)
            label = page_list[e.control.selected_index]
            page.add(pages_dict[label])
            page.update()
        
        # نوار ناوبری
        nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon="HOME", label="خانه"),
                ft.NavigationDestination(icon="LIST", label="کارها"),
                ft.NavigationDestination(icon="CALENDAR_MONTH", label="تقویم"),
                ft.NavigationDestination(icon="GRID_VIEW", label="آیزنهاور"),
                ft.NavigationDestination(icon="TIMER", label="پومودورو"),
                ft.NavigationDestination(icon="REPEAT", label="عادت‌ها"),
                ft.NavigationDestination(icon="FLAG", label="اهداف"),
                ft.NavigationDestination(icon="FOCUS_MODE", label="تمرکز"),
                ft.NavigationDestination(icon="ENERGY_SAVINGS_LEAF", label="انرژی"),
                ft.NavigationDestination(icon="BAR_CHART", label="گزارش‌ها"),
                ft.NavigationDestination(icon="SETTINGS", label="تنظیمات"),
                ft.NavigationDestination(icon="HELP", label="راهنما"),
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
        
    except Exception as e:
        # نمایش خطا در صفحه
        error_text = traceback.format_exc()
        page.controls.clear()
        page.add(
            ft.Text("❌ خطا در اجرای برنامه:", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700),
            ft.Text(str(e), size=16, color=ft.Colors.RED_400),
            ft.Container(
                content=ft.Text(error_text, size=12, color=ft.Colors.GREY_600),
                padding=10,
                bgcolor=ft.Colors.GREY_100,
                border_radius=10,
            ),
        )
        page.update()
        print(error_text)

if __name__ == "__main__":
    ft.app(target=main)
