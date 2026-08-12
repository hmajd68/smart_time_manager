# pages/pomodoro.py
import flet as ft
from managers.pomodoro_manager import PomodoroManager
from managers.gamification_manager import GamificationManager

class PomodoroPage:
    def __init__(self, page: ft.Page, pomodoro_manager: PomodoroManager, gamification: GamificationManager):
        self.page = page
        self.pomodoro = pomodoro_manager
        self.gamification = gamification
        
        # ایجاد ویجت‌ها در __init__
        self.time_display = ft.Text(
            "25:00",
            size=60,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.PINK_700
        )
        
        self.status_text = ft.Text(
            "⏰ آماده شروع",
            size=16,
            color=ft.Colors.GREY_600
        )
        
        self.session_counter = ft.Text(
            "جلسات امروز: 0",
            size=14,
            color=ft.Colors.GREY_600
        )
        
        self.work_input = ft.TextField(
            value="25",
            width=50,
            text_align=ft.TextAlign.CENTER,
            on_change=self.update_work_time,
            hint_text="کار"
        )
        
        self.break_input = ft.TextField(
            value="5",
            width=50,
            text_align=ft.TextAlign.CENTER,
            on_change=self.update_break_time,
            hint_text="استراحت"
        )
        
        self.content = None
        self.build()
    
    def build(self):
        # دکمه‌های کنترل
        controls = ft.Row([
            ft.IconButton(
                icon="PLAY_CIRCLE",
                icon_size=50,
                icon_color=ft.Colors.GREEN_700,
                on_click=self.start_pomodoro,
                tooltip="شروع"
            ),
            ft.IconButton(
                icon="PAUSE_CIRCLE",
                icon_size=50,
                icon_color=ft.Colors.ORANGE_700,
                on_click=self.pause_pomodoro,
                tooltip="مکث"
            ),
            ft.IconButton(
                icon="STOP_CIRCLE",
                icon_size=50,
                icon_color=ft.Colors.RED_700,
                on_click=self.stop_pomodoro,
                tooltip="توقف"
            ),
            ft.IconButton(
                icon="REFRESH",
                icon_size=50,
                icon_color=ft.Colors.BLUE_700,
                on_click=self.reset_pomodoro,
                tooltip="بازنشانی"
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        # تنظیمات زمان
        settings_row = ft.Row([
            ft.Text("⏱️ تنظیمات:", size=14, weight=ft.FontWeight.BOLD),
            self.work_input,
            ft.Text("/", size=16),
            self.break_input,
            ft.Text("دقیقه", size=14),
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        self.content = ft.Column([
            ft.Text("🍅 تایمر پومودورو", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.PINK_700),
            ft.Divider(color=ft.Colors.PINK_200),
            ft.Container(
                content=ft.Column([
                    self.time_display,
                    self.status_text,
                    self.session_counter,
                    controls,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                bgcolor=ft.Colors.PINK_50,
                border_radius=20
            ),
            ft.Divider(height=10),
            settings_row,
            ft.Text("💡 ۴ جلسه تمرکز = ۱ استراحت طولانی", size=12, color=ft.Colors.GREY_500),
        ], scroll=ft.ScrollMode.AUTO)
    
    def start_pomodoro(self, e):
        self.pomodoro.start(
            on_tick=self.update_timer,
            on_complete=self.on_complete,
            on_state_change=self.on_state_change
        )
        self.status_text.value = "🔴 در حال تمرکز..."
        self.status_text.update()
    
    def pause_pomodoro(self, e):
        self.pomodoro.pause()
        self.status_text.value = "⏸️ مکث"
        self.status_text.update()
    
    def stop_pomodoro(self, e):
        self.pomodoro.stop()
        self.status_text.value = "⏹️ متوقف شد"
        self.status_text.update()
    
    def reset_pomodoro(self, e):
        self.pomodoro.reset()
        self.time_display.value = "25:00"
        self.time_display.color = ft.Colors.PINK_700
        self.status_text.value = "⏰ آماده شروع"
        self.status_text.update()
        self.time_display.update()
    
    def update_timer(self, remaining, is_work):
        minutes = remaining // 60
        seconds = remaining % 60
        self.time_display.value = f"{minutes:02d}:{seconds:02d}"
        self.time_display.color = ft.Colors.GREEN_700 if is_work else ft.Colors.ORANGE_700
        self.time_display.update()
    
    def on_complete(self, is_work, remaining, message):
        self.status_text.value = f"✅ {message} تمام شد!"
        self.status_text.update()
        self.gamification.add_points(10, "پومودورو")
        self.update_session_counter()
        
        # نمایش اعلان
        self.page.snack_bar = ft.SnackBar(
            ft.Text(f"🎉 {message}! +۱۰ امتیاز"),
            bgcolor=ft.Colors.PINK_700
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def on_state_change(self, state, remaining):
        states = {
            'running': '🔴 در حال اجرا...',
            'paused': '⏸️ مکث',
            'stopped': '⏹️ متوقف شد',
            'reset': '🔄 بازنشانی شد'
        }
        self.status_text.value = states.get(state, state)
        self.status_text.update()
    
    def update_session_counter(self):
        # به‌روزرسانی بدون نیاز به update() در اینجا
        sessions, total_time = self.pomodoro.get_today_sessions()
        self.session_counter.value = f"📊 جلسات امروز: {sessions} | زمان کل: {total_time//60} دقیقه"
        # اگر صفحه وجود دارد، به‌روزرسانی کن
        if self.content and self.content.page:
            self.session_counter.update()
    
    def update_work_time(self, e):
        try:
            value = int(e.control.value)
            if 1 <= value <= 60:
                self.pomodoro.work_time = value * 60
                if self.pomodoro.is_work and not self.pomodoro.is_running:
                    self.time_display.value = f"{value:02d}:00"
                    self.time_display.update()
        except:
            pass
    
        self.page.add(self.content)
    def update_break_time(self, e):
        try:
            value = int(e.control.value)
            if 1 <= value <= 30:
                self.pomodoro.break_time = value * 60
        except:
            pass
