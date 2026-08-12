# pages/reports.py
import flet as ft
from managers.task_manager import TaskManager
from managers.gamification_manager import GamificationManager
from managers.habit_manager import HabitManager
from managers.pomodoro_manager import PomodoroManager
from datetime import datetime, timedelta

class ReportsPage:
    def __init__(self, page: ft.Page, task_manager: TaskManager, gamification: GamificationManager,
                 habit_manager: HabitManager, pomodoro_manager: PomodoroManager):
        self.page = page
        self.task_manager = task_manager
        self.gamification = gamification
        self.habit_manager = habit_manager
        self.pomodoro_manager = pomodoro_manager
        
        # ایجاد ویجت‌ها
        self.content_container = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.selected_tab = "daily"
        
        # دکمه‌های تب به جای Tabs
        self.tab_row = ft.Row([
            ft.ElevatedButton(
                "📊 روزانه",
                on_click=lambda _: self.change_tab("daily"),
                bgcolor=ft.Colors.PINK_700 if self.selected_tab == "daily" else ft.Colors.GREY_200,
                color=ft.Colors.WHITE if self.selected_tab == "daily" else ft.Colors.BLACK
            ),
            ft.ElevatedButton(
                "📈 هفتگی",
                on_click=lambda _: self.change_tab("weekly"),
                bgcolor=ft.Colors.PINK_700 if self.selected_tab == "weekly" else ft.Colors.GREY_200,
                color=ft.Colors.WHITE if self.selected_tab == "weekly" else ft.Colors.BLACK
            ),
            ft.ElevatedButton(
                "📉 ماهانه",
                on_click=lambda _: self.change_tab("monthly"),
                bgcolor=ft.Colors.PINK_700 if self.selected_tab == "monthly" else ft.Colors.GREY_200,
                color=ft.Colors.WHITE if self.selected_tab == "monthly" else ft.Colors.BLACK
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        self.content = ft.Column([
            ft.Text("📊 گزارش عملکرد", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.PINK_700),
            ft.Divider(height=10),
            self.tab_row,
            ft.Divider(height=10),
            self.content_container,
        ], scroll=ft.ScrollMode.AUTO)
        
        # اضافه کردن به صفحه
        self.page.add(self.content)
        self.show_daily_report()
    
    def change_tab(self, tab):
        self.selected_tab = tab
        # به‌روزرسانی رنگ دکمه‌ها
        for i, btn in enumerate(self.tab_row.controls):
            if i == 0:
                btn.bgcolor = ft.Colors.PINK_700 if tab == "daily" else ft.Colors.GREY_200
                btn.color = ft.Colors.WHITE if tab == "daily" else ft.Colors.BLACK
            elif i == 1:
                btn.bgcolor = ft.Colors.PINK_700 if tab == "weekly" else ft.Colors.GREY_200
                btn.color = ft.Colors.WHITE if tab == "weekly" else ft.Colors.BLACK
            else:
                btn.bgcolor = ft.Colors.PINK_700 if tab == "monthly" else ft.Colors.GREY_200
                btn.color = ft.Colors.WHITE if tab == "monthly" else ft.Colors.BLACK
        
        self.content_container.controls.clear()
        if tab == "daily":
            self.show_daily_report()
        elif tab == "weekly":
            self.show_weekly_report()
        else:
            self.show_monthly_report()
        self.page.update()
    
    def show_daily_report(self):
        self.content_container.controls.clear()
        
        stats = self.task_manager.get_stats()
        g_status = self.gamification.get_status()
        habit_stats = self.habit_manager.get_stats()
        sessions, total_time = self.pomodoro_manager.get_today_sessions()
        
        cards = ft.Row([
            self._stat_card("📋", stats['total'], "کل کارها"),
            self._stat_card("✅", stats['done'], "انجام شده"),
            self._stat_card("⭐", g_status['points'], "امتیاز"),
            self._stat_card("🍅", sessions, "پومودورو"),
        ], alignment=ft.MainAxisAlignment.CENTER, wrap=True)
        
        progress_card = ft.Card(
            ft.Container(
                ft.Column([
                    ft.Text("پیشرفت امروز", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{stats['completion_rate']:.1f}%", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.PINK_700),
                    ft.ProgressBar(value=stats['completion_rate']/100, height=10, color=ft.Colors.PINK_700),
                ]),
                padding=15
            )
        )
        
        gamification_card = ft.Card(
            ft.Container(
                ft.Column([
                    ft.Text("🏆 گیمیفیکیشن", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"سطح: {g_status['level']} | رکورد: {g_status['streak']} روز"),
                    ft.Text(f"زمان تمرکز: {g_status['total_focus_time']} دقیقه"),
                    ft.Text(f"نشان‌ها: {', '.join(g_status['badges']) if g_status['badges'] else 'هیچ'}", 
                           size=12, color=ft.Colors.GREY_600),
                ]),
                padding=15
            )
        )
        
        habit_card = ft.Card(
            ft.Container(
                ft.Column([
                    ft.Text("🔄 عادت‌ها", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"کل: {habit_stats['total']} | امروز: {habit_stats['done_today']}"),
                    ft.Text(f"موفقیت: {habit_stats['completion_rate']:.0f}%"),
                    ft.Text(f"بهترین رکورد: {habit_stats['best_streak']} روز", size=12, color=ft.Colors.GREY_600),
                ]),
                padding=15
            )
        )
        
        pomodoro_card = ft.Card(
            ft.Container(
                ft.Column([
                    ft.Text("🍅 پومودورو", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"جلسات امروز: {sessions}"),
                    ft.Text(f"زمان کل: {total_time//60} دقیقه"),
                ]),
                padding=15
            )
        )
        
        self.content_container.controls.extend([
            cards,
            progress_card,
            gamification_card,
            habit_card,
            pomodoro_card,
        ])
        self.page.update()
    
    def show_weekly_report(self):
        self.content_container.controls.clear()
        
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        weekly_tasks = 0
        weekly_done = 0
        
        for task in self.task_manager.get_all():
            if task.created_at and task.created_at >= week_ago:
                weekly_tasks += 1
                if task.done:
                    weekly_done += 1
        
        weekly_progress = (weekly_done / weekly_tasks * 100) if weekly_tasks > 0 else 0
        
        self.content_container.controls.append(
            ft.Text("📈 گزارش هفتگی", size=20, weight=ft.FontWeight.BOLD)
        )
        self.content_container.controls.append(
            ft.Row([
                self._stat_card("📋", weekly_tasks, "کل کارها"),
                self._stat_card("✅", weekly_done, "انجام شده"),
            ], alignment=ft.MainAxisAlignment.CENTER, wrap=True)
        )
        self.content_container.controls.append(
            ft.Text(f"پیشرفت هفتگی: {weekly_progress:.1f}%", size=16, weight=ft.FontWeight.BOLD)
        )
        self.content_container.controls.append(
            ft.ProgressBar(value=weekly_progress/100, height=10, color=ft.Colors.PINK_700)
        )
        self.page.update()
    
    def show_monthly_report(self):
        self.content_container.controls.clear()
        
        month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        monthly_tasks = 0
        monthly_done = 0
        
        for task in self.task_manager.get_all():
            if task.created_at and task.created_at >= month_ago:
                monthly_tasks += 1
                if task.done:
                    monthly_done += 1
        
        monthly_progress = (monthly_done / monthly_tasks * 100) if monthly_tasks > 0 else 0
        
        self.content_container.controls.append(
            ft.Text("📉 گزارش ماهانه", size=20, weight=ft.FontWeight.BOLD)
        )
        self.content_container.controls.append(
            ft.Row([
                self._stat_card("📋", monthly_tasks, "کل کارها"),
                self._stat_card("✅", monthly_done, "انجام شده"),
            ], alignment=ft.MainAxisAlignment.CENTER, wrap=True)
        )
        self.content_container.controls.append(
            ft.Text(f"پیشرفت ماهانه: {monthly_progress:.1f}%", size=16, weight=ft.FontWeight.BOLD)
        )
        self.content_container.controls.append(
            ft.ProgressBar(value=monthly_progress/100, height=10, color=ft.Colors.PINK_700)
        )
        self.page.update()
    
    def _stat_card(self, icon, value, label):
        return ft.Card(
            ft.Container(
                ft.Column([
                    ft.Text(icon, size=20),
                    ft.Text(str(value), size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=10,
                width=80
            ),
            elevation=2
        )
