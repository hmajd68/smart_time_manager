# pages/focus.py
import flet as ft
from managers.gamification_manager import GamificationManager
import threading
import time

class FocusPage:
    def __init__(self, page: ft.Page, gamification: GamificationManager):
        self.page = page
        self.gamification = gamification
        self.is_running = False
        self.is_paused = False
        self.elapsed_time = 0
        self.thread = None
        self.build()
    
    def build(self):
        # نمایش زمان
        self.time_display = ft.Text(
            "00:00:00",
            size=60,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.PINK_700
        )
        
        # وضعیت
        self.status_text = ft.Text(
            "⏸️ آماده شروع",
            size=16,
            color=ft.Colors.GREY_600
        )
        
        # آمار
        g_status = self.gamification.get_status()
        self.stats_text = ft.Text(
            f"📊 زمان کل تمرکز: {g_status['total_focus_time']} دقیقه",
            size=14,
            color=ft.Colors.GREY_600
        )
        
        # دکمه‌های کنترل
        controls = ft.Row([
            ft.IconButton(
                icon="PLAY_CIRCLE",
                icon_size=50,
                icon_color=ft.Colors.GREEN_700,
                on_click=self.start_focus,
                tooltip="شروع"
            ),
            ft.IconButton(
                icon="PAUSE_CIRCLE",
                icon_size=50,
                icon_color=ft.Colors.ORANGE_700,
                on_click=self.pause_focus,
                tooltip="مکث"
            ),
            ft.IconButton(
                icon="STOP_CIRCLE",
                icon_size=50,
                icon_color=ft.Colors.RED_700,
                on_click=self.stop_focus,
                tooltip="توقف"
            ),
            ft.IconButton(
                icon="REFRESH",
                icon_size=50,
                icon_color=ft.Colors.BLUE_700,
                on_click=self.reset_focus,
                tooltip="بازنشانی"
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        self.content = ft.Column([
            ft.Text("🎯 حالت تمرکز", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.PINK_700),
            ft.Divider(color=ft.Colors.PINK_200),
            ft.Container(
                content=ft.Column([
                    self.time_display,
                    self.status_text,
                    self.stats_text,
                    controls,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                bgcolor=ft.Colors.PINK_50,
                border_radius=20
            ),
            ft.Text("💡 بدون وقفه کار کن و تمرکز خودت رو افزایش بده", size=12, color=ft.Colors.GREY_500),
        ], scroll=ft.ScrollMode.AUTO)
    
    def start_focus(self, e):
        if not self.is_running and not self.is_paused:
            self.is_running = True
            self.is_paused = False
            self.status_text.value = "🔴 در حال تمرکز..."
            self.status_text.update()
            self.thread = threading.Thread(target=self._run_focus, daemon=True)
            self.thread.start()
    
    def pause_focus(self, e):
        if self.is_running:
            self.is_running = False
            self.is_paused = True
            self.status_text.value = "⏸️ مکث"
            self.status_text.update()
    
    def stop_focus(self, e):
        if self.is_running or self.is_paused:
            self.is_running = False
            self.is_paused = False
            minutes = self.elapsed_time // 60
            if minutes > 0:
                self.gamification.add_focus_time(minutes)
                self.gamification.add_points(minutes // 5, f"{minutes} دقیقه تمرکز")
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"🎯 {minutes} دقیقه تمرکز! +{minutes//5} امتیاز"),
                    bgcolor=ft.Colors.PINK_700
                )
                self.page.snack_bar.open = True
                self.page.update()
            self.status_text.value = "⏹️ متوقف شد"
            self.status_text.update()
            self.update_stats()
    
    def reset_focus(self, e):
        self.is_running = False
        self.is_paused = False
        self.elapsed_time = 0
        self.time_display.value = "00:00:00"
        self.time_display.color = ft.Colors.PINK_700
        self.status_text.value = "⏸️ آماده شروع"
        self.status_text.update()
        self.time_display.update()
    
    def _run_focus(self):
        while self.is_running:
            time.sleep(1)
            self.elapsed_time += 1
            
            hours = self.elapsed_time // 3600
            minutes = (self.elapsed_time % 3600) // 60
            seconds = self.elapsed_time % 60
            
            self.time_display.value = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.time_display.color = ft.Colors.GREEN_700 if self.elapsed_time > 0 else ft.Colors.PINK_700
            self.time_display.update()
    
        self.page.add(self.content)
    def update_stats(self):
        g_status = self.gamification.get_status()
        self.stats_text.value = f"📊 زمان کل تمرکز: {g_status['total_focus_time']} دقیقه"
        self.stats_text.update()
