# pages/habits.py
import flet as ft
from managers.habit_manager import HabitManager
from managers.gamification_manager import GamificationManager
from datetime import datetime

class HabitsPage:
    def __init__(self, page: ft.Page, habit_manager: HabitManager, gamification: GamificationManager):
        self.page = page
        self.habit_manager = habit_manager
        self.gamification = gamification
        self.habit_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        
        # فیلد ورودی
        self.name_input = ft.TextField(
            hint_text="نام عادت جدید...",
            width=300,
            border_color=ft.Colors.PURPLE_400,
            focused_border_color=ft.Colors.PURPLE_700,
            on_submit=lambda _: self.add_habit(None),
        )
        
        # دکمه افزودن
        self.add_btn = ft.ElevatedButton(
            "➕ افزودن عادت",
            on_click=self.add_habit,
            bgcolor=ft.Colors.PURPLE_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )
        
        self.build()
    
    def build(self):
        self.content = ft.Column([
            ft.Row([
                ft.Text("🔄 مدیریت عادت‌ها", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(color=ft.Colors.PURPLE_200),
            
            ft.Row([
                self.name_input,
                self.add_btn,
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
            
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            
            ft.Text("📌 لیست عادت‌ها:", size=18, weight=ft.FontWeight.BOLD),
            self.habit_list,
            
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.page.add(self.content)
        self.update_list()
    
    def add_habit(self, e):
        name = self.name_input.value
        if not name or not name.strip():
            self._show_message("⚠️ نام عادت را وارد کن!", ft.Colors.RED_400)
            return
        
        try:
            self.habit_manager.add(name.strip())
            self.gamification.add_points(10)
            self.name_input.value = ""
            self.name_input.update()
            self.update_list()
            self._show_message("✅ عادت جدید اضافه شد! +۱۰ امتیاز", ft.Colors.GREEN_700)
        except Exception as err:
            self._show_message(f"❌ خطا: {str(err)}", ft.Colors.RED_400)
    
    def update_list(self):
        self.habit_list.controls.clear()
        habits = self.habit_manager.get_all()
        
        if not habits:
            self.habit_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name="REPEAT", size=50, color=ft.Colors.GREY_300),
                        ft.Text("هیچ عادتی ثبت نشده!", size=16, color=ft.Colors.GREY_500),
                        ft.Text("یک عادت جدید اضافه کن", size=12, color=ft.Colors.GREY_400),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30,
                )
            )
        else:
            for habit in habits:
                self.habit_list.controls.append(self._make_card(habit))
        
        self.page.update()
    
    def _make_card(self, habit):
        today = datetime.now().strftime("%Y-%m-%d")
        is_done_today = habit.last_done == today
        
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Icon(
                        name="CHECK_CIRCLE" if is_done_today else "CHECK_CIRCLE_OUTLINE",
                        color=ft.Colors.GREEN_700 if is_done_today else ft.Colors.GREY_400,
                        size=30,
                    ),
                    ft.Text(
                        habit.name,
                        size=16,
                        weight=ft.FontWeight.BOLD if not is_done_today else ft.FontWeight.NORMAL,
                        expand=True,
                    ),
                    ft.Text(f"🔥 {habit.streak} روز", size=14, color=ft.Colors.ORANGE_700),
                    ft.IconButton(
                        icon="CHECK",
                        icon_color=ft.Colors.GREEN_700,
                        on_click=lambda e, h=habit: self.mark_done(h.id),
                        disabled=is_done_today,
                    ),
                    ft.IconButton(
                        icon="DELETE",
                        icon_color=ft.Colors.RED_400,
                        on_click=lambda e, h=habit: self.delete_habit(h.id),
                    ),
                ]),
                padding=10,
            ),
            elevation=2,
            margin=ft.margin.only(bottom=5),
        )
    
    def mark_done(self, habit_id):
        streak = self.habit_manager.mark_done(habit_id)
        self.gamification.add_points(5)
        self.update_list()
        self._show_message(f"✅ عادت ثبت شد! 🔥 {streak} روز متوالی", ft.Colors.GREEN_700)
    
    def delete_habit(self, habit_id):
        if self.habit_manager.delete(habit_id):
            self.update_list()
            self._show_message("🗑️ عادت حذف شد", ft.Colors.ORANGE_700)
    
    def _show_message(self, msg, color):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color, duration=2000)
        self.page.snack_bar.open = True
        self.page.update()
