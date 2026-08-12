# pages/eisenhower.py
import flet as ft
from managers.task_manager import TaskManager

class EisenhowerPage:
    def __init__(self, page: ft.Page, task_manager: TaskManager):
        self.page = page
        self.task_manager = task_manager
        self.build()
    
    def build(self):
        # تعریف ۴ بخش ماتریس
        quadrants = [
            {
                "title": "🔴 مهم و فوری",
                "type": "مهم و فوری",
                "color": ft.Colors.RED_100,
                "border_color": ft.Colors.RED_400,
                "action": "انجام بده"
            },
            {
                "title": "🟡 مهم و غیر فوری",
                "type": "مهم و غیر فوری",
                "color": ft.Colors.YELLOW_100,
                "border_color": ft.Colors.YELLOW_700,
                "action": "برنامه‌ریزی کن"
            },
            {
                "title": "🟠 غیر مهم و فوری",
                "type": "غیر مهم و فوری",
                "color": ft.Colors.ORANGE_100,
                "border_color": ft.Colors.ORANGE_700,
                "action": "واگذار کن"
            },
            {
                "title": "⚪ حذف‌شدنی",
                "type": "حذف‌شدنی",
                "color": ft.Colors.GREY_200,
                "border_color": ft.Colors.GREY_600,
                "action": "حذف کن"
            }
        ]
        
        # ساخت ماتریس
        matrix = ft.Column()
        
        # ردیف اول
        row1 = ft.Row()
        for quad in quadrants[:2]:
            row1.controls.append(self._create_quadrant_card(quad))
        
        # ردیف دوم
        row2 = ft.Row()
        for quad in quadrants[2:]:
            row2.controls.append(self._create_quadrant_card(quad))
        
        matrix.controls.append(row1)
        matrix.controls.append(row2)
        
        self.content = ft.Column([
            ft.Text("ماتریس آیزنهاور", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.PINK_700),
            ft.Text("کارها را بر اساس اولویت و فوریت دسته‌بندی کن", size=14, color=ft.Colors.GREY_700),
            ft.Divider(height=10),
            matrix,
        ], scroll=ft.ScrollMode.AUTO)
    
        self.page.add(self.content)
    def _create_quadrant_card(self, quad):
        tasks = self.task_manager.get_by_eisenhower(quad["type"])
        
        return ft.Card(
            ft.Container(
                content=ft.Column([
                    ft.Text(quad["title"], size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                    ft.Text(f"{quad['action']} - {len(tasks)} کار", size=14, color=ft.Colors.GREY_600),
                    ft.Divider(height=5, color=quad["border_color"]),
                    ft.Column([
                        ft.Text(f"• {task.title}", size=14) for task in tasks[:5]
                    ]) if tasks else ft.Text("خالی!", size=14, color=ft.Colors.GREY_500),
                    ft.Text(f"... {len(tasks) - 5} کار دیگر" if len(tasks) > 5 else "", size=12, color=ft.Colors.GREY_500),
                ]),
                padding=15,
                width=180,
                height=250,
                bgcolor=quad["color"],
                border=ft.border.all(2, quad["border_color"]),
                border_radius=15
            ),
            elevation=3
        )
