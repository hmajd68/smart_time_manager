# pages/tasks.py
import flet as ft
from managers.task_manager import TaskManager
from managers.gamification_manager import GamificationManager
from database.models import Task
from utils.constants import CATEGORIES, PRIORITIES, EISENHOWER_TYPES
from datetime import datetime
import jdatetime

class TasksPage:
    def __init__(self, page: ft.Page, task_manager: TaskManager, gamification: GamificationManager):
        self.page = page
        self.task_manager = task_manager
        self.gamification = gamification
        self.task_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        
        # فیلدهای ورودی
        self.title_input = ft.TextField(
            hint_text="عنوان کار را وارد کن...",
            width=300,
            border_color=ft.Colors.PINK_400,
            focused_border_color=ft.Colors.PINK_700,
            on_submit=lambda _: self.add_task(None),
        )
        
        # ===== تاریخ به صورت نوشتنی =====
        self.deadline_input = ft.TextField(
            hint_text="تاریخ سررسید (مثلاً 1403/01/15)...",
            width=200,
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
        )
        
        self.category_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(cat, cat) for cat in CATEGORIES],
            value="سایر",
            width=120,
            border_color=ft.Colors.PINK_400,
        )
        
        self.priority_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(p, p) for p in PRIORITIES],
            value="متوسط",
            width=120,
            border_color=ft.Colors.PINK_400,
        )
        
        # دکمه افزودن
        self.add_btn = ft.ElevatedButton(
            "➕ افزودن کار",
            on_click=self.add_task,
            bgcolor=ft.Colors.PINK_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )
        
        self.build()
    
    def build(self):
        quick_guide = ft.Container(
            content=ft.Column([
                ft.Text("💡 راهنمای سریع", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.PINK_700),
                ft.Text("• عنوان کار رو وارد کن", size=13, color=ft.Colors.GREY_700),
                ft.Text("• تاریخ رو به فرمت (سال/ماه/روز) وارد کن", size=13, color=ft.Colors.GREY_700),
                ft.Text("• با ✔️ کار انجام شده رو علامت بزن (+۱۰ امتیاز)", size=13, color=ft.Colors.GREY_700),
            ]),
            padding=10,
            bgcolor=ft.Colors.PINK_50,
            border_radius=10,
            margin=ft.margin.only(bottom=10),
        )
        
        self.content = ft.Column([
            ft.Row([
                ft.Text("📋 مدیریت کارها", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.PINK_700),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(color=ft.Colors.PINK_200),
            
            quick_guide,
            
            ft.Column([
                self.title_input,
                ft.Row([
                    self.deadline_input,
                    self.category_dropdown,
                    self.priority_dropdown,
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                ft.Row([self.add_btn], alignment=ft.MainAxisAlignment.CENTER),
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            
            ft.Text("📌 لیست کارها:", size=18, weight=ft.FontWeight.BOLD),
            self.task_list,
            
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.page.add(self.content)
        self.update_list()
    
    def add_task(self, e):
        """افزودن کار جدید"""
        title = self.title_input.value
        deadline_jalali = self.deadline_input.value
        category = self.category_dropdown.value
        priority = self.priority_dropdown.value
        
        if not title or not title.strip():
            self._show_message("⚠️ عنوان کار را وارد کن!", ft.Colors.RED_400)
            return
        
        # تبدیل تاریخ
        deadline_miladi = None
        if deadline_jalali and deadline_jalali.strip():
            try:
                parts = deadline_jalali.strip().split('/')
                if len(parts) == 3:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    jalali_date = jdatetime.date(year, month, day)
                    deadline_miladi = jalali_date.togregorian().strftime("%Y-%m-%d")
            except Exception as err:
                self._show_message("⚠️ تاریخ نامعتبر! (مثال: 1403/01/15)", ft.Colors.RED_400)
                return
        
        try:
            task = Task(
                title=title.strip(),
                category=category,
                priority=priority,
                deadline=deadline_miladi,
                eisenhower_type="مهم و غیر فوری",
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            )
            
            saved = self.task_manager.add(task)
            self.gamification.add_points(5)
            
            self.title_input.value = ""
            self.deadline_input.value = ""
            self.title_input.update()
            self.deadline_input.update()
            
            self.update_list()
            self._show_message("✅ کار اضافه شد! +۵ امتیاز", ft.Colors.GREEN_700)
            
        except Exception as err:
            self._show_message(f"❌ خطا: {str(err)}", ft.Colors.RED_400)
            import traceback
            traceback.print_exc()
    
    def update_list(self):
        """به‌روزرسانی لیست کارها"""
        self.task_list.controls.clear()
        tasks = self.task_manager.get_all()
        
        if not tasks:
            self.task_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name="TASK_ALT", size=50, color=ft.Colors.GREY_300),
                        ft.Text("هیچ کاری نیست!", size=16, color=ft.Colors.GREY_500),
                        ft.Text("یک کار جدید اضافه کن ☝️", size=12, color=ft.Colors.GREY_400),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30,
                )
            )
        else:
            for task in tasks:
                self.task_list.controls.append(self._make_card(task))
        
        self.page.update()
    
    def _make_card(self, task):
        """ساخت کارت نمایش کار"""
        deadline_display = "بدون تاریخ"
        if task.deadline:
            try:
                miladi_date = datetime.strptime(task.deadline, "%Y-%m-%d")
                jalali_date = jdatetime.date.fromgregorian(date=miladi_date)
                deadline_display = jalali_date.strftime("%Y/%m/%d")
            except:
                deadline_display = task.deadline
        
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Checkbox(
                        value=task.done,
                        on_change=lambda e, t=task: self.toggle_task(t.id),
                        fill_color=ft.Colors.PINK_700,
                    ),
                    ft.Column([
                        ft.Text(
                            task.title,
                            size=16,
                            weight=ft.FontWeight.BOLD if not task.done else ft.FontWeight.NORMAL,
                            color=ft.Colors.BLACK if not task.done else ft.Colors.GREY_600,
                        ),
                        ft.Row([
                            ft.Text(f"📅 {deadline_display}", size=12, color=ft.Colors.GREY_500),
                            ft.Text(f"📂 {task.category}", size=12, color=ft.Colors.GREY_500),
                            ft.Text(f"⚡ {task.priority}", size=12, color=ft.Colors.GREY_500),
                        ]),
                    ], expand=True, spacing=2),
                    ft.IconButton(
                        icon="DELETE",
                        icon_color=ft.Colors.RED_400,
                        on_click=lambda e, t=task: self.delete_task(t.id),
                    ),
                ]),
                padding=10,
            ),
            elevation=2,
            margin=ft.margin.only(bottom=5),
        )
    
    def toggle_task(self, task_id):
        if self.task_manager.toggle_done(task_id):
            self.gamification.add_points(10)
            self.update_list()
            self._show_message("🎉 +۱۰ امتیاز!", ft.Colors.GREEN_700)
    
    def delete_task(self, task_id):
        if self.task_manager.delete(task_id):
            self.update_list()
            self._show_message("🗑️ حذف شد", ft.Colors.ORANGE_700)
    
    def _show_message(self, msg, color):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color, duration=2000)
        self.page.snack_bar.open = True
        self.page.update()
