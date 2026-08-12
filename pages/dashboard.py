# pages/dashboard.py
import flet as ft
from managers.task_manager import TaskManager
from managers.gamification_manager import GamificationManager
from managers.habit_manager import HabitManager
from services.ai_service import AIService
from utils.date_utils import DateUtils
from utils.constants import CATEGORIES, PRIORITIES

class DashboardPage:
    def __init__(self, page: ft.Page, task_manager: TaskManager, gamification: GamificationManager, 
                 habit_manager: HabitManager):
        self.page = page
        self.task_manager = task_manager
        self.gamification = gamification
        self.habit_manager = habit_manager
        self.ai_service = AIService(task_manager)
        self.build()
    
    def build(self):
        stats = self.task_manager.get_stats()
        g_status = self.gamification.get_status()
        habit_stats = self.habit_manager.get_stats()
        
        # هدر سلام
        header = ft.Container(
            content=ft.Column([
                ft.Text("سلام 👋", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.PINK_700),
                ft.Text("امروز برای موفقیت آماده‌ای؟", size=16, color=ft.Colors.GREY_700),
                ft.Text(DateUtils.get_today_jalali(), size=14, color=ft.Colors.GREY_600),
            ]),
            padding=10
        )
        
        # کارت‌های آماری
        stat_cards = ft.Row([
            self._stat_card("📋", f"{stats['total']}", "کل کارها", ft.Colors.BLUE_100),
            self._stat_card("✅", f"{stats['done']}", "انجام شده", ft.Colors.GREEN_100),
            self._stat_card("⏳", f"{stats['pending']}", "باقی‌مانده", ft.Colors.ORANGE_100),
            self._stat_card("⭐", f"{g_status['points']}", "امتیاز", ft.Colors.PINK_100),
        ], alignment=ft.MainAxisAlignment.CENTER, wrap=True)
        
        # پیشرفت
        progress = ft.Container(
            content=ft.Column([
                ft.Text(f"پیشرفت: {stats['completion_rate']:.1f}%", size=16, weight=ft.FontWeight.BOLD),
                ft.ProgressBar(value=stats['completion_rate']/100, height=10, color=ft.Colors.PINK_700),
            ]),
            padding=10
        )
        
        # برنامه امروز
        today_tasks = self.task_manager.get_today_tasks()
        today_section = ft.Card(
            ft.Container(
                content=ft.Column([
                    ft.Text("📌 برنامه امروز", size=18, weight=ft.FontWeight.BOLD),
                    ft.Column([
                        self._task_item(task) for task in today_tasks[:5]
                    ]) if today_tasks else ft.Text("🎉 امروز کاری نداری!", color=ft.Colors.GREY_600),
                ]),
                padding=15
            )
        )
        
        # پیشنهاد هوشمند
        ai_plan = self.ai_service.get_daily_plan("متوسط")
        ai_card = ft.Card(
            ft.Container(
                content=ft.Column([
                    ft.Text("🤖 پیشنهاد هوشمند امروز", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700),
                    ft.Text(ai_plan['message'], size=14, color=ft.Colors.GREY_800),
                    ft.Column([
                        ft.Text(f"• {suggestion}", size=14, color=ft.Colors.GREY_700) 
                        for suggestion in ai_plan['suggestions'][:3]
                    ]) if ai_plan['suggestions'] else ft.Text(""),
                ]),
                padding=15,
                bgcolor=ft.Colors.PURPLE_50
            )
        )
        
        # صفحه
        self.content = ft.Column([
            header,
            stat_cards,
            progress,
            ft.Divider(height=10),
            today_section,
            ft.Divider(height=10),
            ai_card,
        ], scroll=ft.ScrollMode.AUTO)
    
    def _stat_card(self, icon, value, label, color):
        return ft.Card(
            ft.Container(
                content=ft.Column([
                    ft.Text(icon, size=24),
                    ft.Text(value, size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                padding=10,
                width=80,
                bgcolor=color,
                border_radius=10
            ),
            elevation=2
        )
    
        self.page.add(self.content)
    def _task_item(self, task):
        priority_icons = {"بالا": "🔴", "متوسط": "🟡", "پایین": "🟢"}
        return ft.Container(
            content=ft.Row([
                ft.Text(priority_icons.get(task.priority, "🟡"), size=16),
                ft.Text(task.title, size=14, expand=True),
                ft.Text(task.category, size=12, color=ft.Colors.GREY_600),
            ]),
            padding=5,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8
        )
