# pages/goals.py
import flet as ft
from managers.goal_manager import GoalManager
from managers.gamification_manager import GamificationManager
from datetime import datetime

class GoalsPage:
    def __init__(self, page: ft.Page, goal_manager: GoalManager, gamification: GamificationManager):
        self.page = page
        self.goal_manager = goal_manager
        self.gamification = gamification
        self.goal_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        
        # فیلدهای ورودی
        self.title_input = ft.TextField(
            hint_text="عنوان هدف...",
            width=300,
            border_color=ft.Colors.ORANGE_400,
            focused_border_color=ft.Colors.ORANGE_700,
            on_submit=lambda _: self.add_goal(None),
        )
        
        self.desc_input = ft.TextField(
            hint_text="توضیحات (اختیاری)...",
            width=300,
            border_color=ft.Colors.ORANGE_400,
            focused_border_color=ft.Colors.ORANGE_700,
            multiline=True,
            max_lines=2,
        )
        
        self.target_date_input = ft.TextField(
            hint_text="تاریخ هدف (مثلاً 1404-01-01)...",
            width=200,
            border_color=ft.Colors.ORANGE_400,
            focused_border_color=ft.Colors.ORANGE_700,
        )
        
        # دکمه افزودن
        self.add_btn = ft.ElevatedButton(
            "➕ افزودن هدف",
            on_click=self.add_goal,
            bgcolor=ft.Colors.ORANGE_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )
        
        self.build()
    
    def build(self):
        self.content = ft.Column([
            ft.Row([
                ft.Text("🎯 مدیریت اهداف", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(color=ft.Colors.ORANGE_200),
            
            ft.Column([
                self.title_input,
                self.desc_input,
                ft.Row([
                    self.target_date_input,
                    self.add_btn,
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            
            ft.Text("📌 لیست اهداف:", size=18, weight=ft.FontWeight.BOLD),
            self.goal_list,
            
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.page.add(self.content)
        self.update_list()
    
    def add_goal(self, e):
        title = self.title_input.value
        if not title or not title.strip():
            self._show_message("⚠️ عنوان هدف را وارد کن!", ft.Colors.RED_400)
            return
        
        try:
            desc = self.desc_input.value or ""
            target_date = self.target_date_input.value or None
            
            self.goal_manager.add(title.strip(), desc, "کوتاه‌مدت", target_date)
            self.gamification.add_points(10)
            
            self.title_input.value = ""
            self.desc_input.value = ""
            self.target_date_input.value = ""
            self.title_input.update()
            self.desc_input.update()
            self.target_date_input.update()
            
            self.update_list()
            self._show_message("✅ هدف جدید اضافه شد! +۱۰ امتیاز", ft.Colors.GREEN_700)
        except Exception as err:
            self._show_message(f"❌ خطا: {str(err)}", ft.Colors.RED_400)
    
    def update_list(self):
        self.goal_list.controls.clear()
        goals = self.goal_manager.get_all()
        
        if not goals:
            self.goal_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name="FLAG", size=50, color=ft.Colors.GREY_300),
                        ft.Text("هیچ هدفی ثبت نشده!", size=16, color=ft.Colors.GREY_500),
                        ft.Text("یک هدف جدید اضافه کن", size=12, color=ft.Colors.GREY_400),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30,
                )
            )
        else:
            for goal in goals:
                self.goal_list.controls.append(self._make_card(goal))
        
        self.page.update()
    
    def _make_card(self, goal):
        progress_color = (
            ft.Colors.GREEN_700 if goal.progress >= 80 else
            ft.Colors.ORANGE_700 if goal.progress >= 50 else
            ft.Colors.RED_700
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(
                            goal.title,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            expand=True,
                        ),
                        ft.Text(f"{goal.progress}%", size=14, weight=ft.FontWeight.BOLD, color=progress_color),
                    ]),
                    ft.Text(goal.description or "بدون توضیحات", size=13, color=ft.Colors.GREY_600),
                    ft.Text(f"📅 {goal.target_date or 'نامشخص'}", size=12, color=ft.Colors.GREY_500),
                    ft.Row([
                        ft.Text(f"پیشرفت:", size=12),
                        ft.ProgressBar(
                            value=goal.progress / 100,
                            width=150,
                            height=8,
                            color=progress_color,
                            bgcolor=ft.Colors.GREY_200,
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([
                        ft.IconButton(
                            icon="REMOVE",
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, g=goal: self.update_progress(g.id, -10),
                            tooltip="کم کردن پیشرفت",
                        ),
                        ft.Slider(
                            min=0,
                            max=100,
                            value=goal.progress,
                            divisions=10,
                            label="{value}%",
                            on_change=lambda e, g=goal: self.update_progress(g.id, int(e.control.value)),
                            thumb_color=ft.Colors.ORANGE_700,
                            active_color=progress_color,
                            width=200,
                        ),
                        ft.IconButton(
                            icon="ADD",
                            icon_color=ft.Colors.GREEN_700,
                            on_click=lambda e, g=goal: self.update_progress(g.id, 10),
                            tooltip="افزایش پیشرفت",
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([
                        ft.Text(f"مراحل:", size=12, weight=ft.FontWeight.BOLD),
                        ft.TextButton(
                            "➕ افزودن مرحله",
                            on_click=lambda e, g=goal: self.add_step_dialog(g.id),
                            style=ft.ButtonStyle(
                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            ),
                        ),
                    ]),
                    ft.Column([
                        ft.Text(f"• {step}", size=12, color=ft.Colors.GREY_600) 
                        for step in (goal.steps or [])[:3]
                    ]) if goal.steps else ft.Text("هیچ مرحله‌ای تعریف نشده", size=12, color=ft.Colors.GREY_400),
                    ft.IconButton(
                        icon="DELETE",
                        icon_color=ft.Colors.RED_400,
                        on_click=lambda e, g=goal: self.delete_goal(g.id),
                    ),
                ]),
                padding=12,
            ),
            elevation=2,
            margin=ft.margin.only(bottom=8),
        )
    
    def update_progress(self, goal_id, value):
        if isinstance(value, int):
            # اگر مقدار مستقیم داده شده
            if value < 0:  # کاهش
                new_progress = max(0, self._get_goal(goal_id).progress + value)
            else:  # افزایش
                new_progress = min(100, value)
        else:
            new_progress = value
        
        self.goal_manager.update_progress(goal_id, new_progress)
        
        # بررسی تکمیل هدف
        goal = self._get_goal(goal_id)
        if goal and goal.progress >= 100:
            self.gamification.add_points(20)
            self._show_message("🎉 هدف کامل شد! +۲۰ امتیاز", ft.Colors.GREEN_700)
        
        self.update_list()
    
    def _get_goal(self, goal_id):
        for goal in self.goal_manager.get_all():
            if goal.id == goal_id:
                return goal
        return None
    
    def add_step_dialog(self, goal_id):
        step_input = ft.TextField(
            hint_text="عنوان مرحله...",
            width=250,
            border_color=ft.Colors.ORANGE_400,
        )
        
        def add_step(e):
            if step_input.value and step_input.value.strip():
                self.goal_manager.add_step(goal_id, step_input.value.strip())
                self.update_list()
                self._show_message("✅ مرحله اضافه شد!", ft.Colors.GREEN_700)
                dialog.open = False
                self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("➕ افزودن مرحله جدید", color=ft.Colors.ORANGE_700),
            content=ft.Column([step_input], tight=True),
            actions=[
                ft.TextButton("لغو", on_click=lambda _: self.close_dialog(dialog)),
                ft.ElevatedButton(
                    "افزودن",
                    on_click=add_step,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                ),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def delete_goal(self, goal_id):
        if self.goal_manager.delete(goal_id):
            self.update_list()
            self._show_message("🗑️ هدف حذف شد", ft.Colors.ORANGE_700)
    
    def _show_message(self, msg, color):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color, duration=2000)
        self.page.snack_bar.open = True
        self.page.update()
