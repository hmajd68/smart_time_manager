# pages/settings.py
import flet as ft
from database.database import Database
from managers.gamification_manager import GamificationManager
from managers.task_manager import TaskManager
from managers.habit_manager import HabitManager
from managers.goal_manager import GoalManager
import csv
from datetime import datetime
import jdatetime

class SettingsPage:
    def __init__(self, page: ft.Page, db: Database, gamification: GamificationManager, 
                 task_manager: TaskManager = None, habit_manager: HabitManager = None, 
                 goal_manager: GoalManager = None):
        self.page = page
        self.db = db
        self.gamification = gamification
        self.task_manager = task_manager
        self.habit_manager = habit_manager
        self.goal_manager = goal_manager
        self.build()
    
    def build(self):
        # دریافت تنظیمات
        self.db.cursor.execute('SELECT * FROM settings')
        settings = self.db.cursor.fetchone()
        
        if settings:
            theme = settings['theme']
            pomodoro_work = settings['pomodoro_work']
            pomodoro_break = settings['pomodoro_break']
            pomodoro_long_break = settings['pomodoro_long_break']
        else:
            theme = 'light'
            pomodoro_work = 25
            pomodoro_break = 5
            pomodoro_long_break = 15
        
        # Theme toggle
        self.theme_toggle = ft.Switch(
            value=theme == 'dark',
            on_change=self.toggle_theme,
            label="🌙 حالت تاریک"
        )
        
        # تنظیمات پومودورو
        self.work_input = ft.TextField(
            value=str(pomodoro_work),
            width=60,
            text_align=ft.TextAlign.CENTER,
            on_change=self.update_settings
        )
        self.break_input = ft.TextField(
            value=str(pomodoro_break),
            width=60,
            text_align=ft.TextAlign.CENTER,
            on_change=self.update_settings
        )
        self.long_break_input = ft.TextField(
            value=str(pomodoro_long_break),
            width=60,
            text_align=ft.TextAlign.CENTER,
            on_change=self.update_settings
        )
        
        # ===== دکمه خروجی Excel =====
        export_excel_button = ft.ElevatedButton(
            "📊 خروجی Excel",
            on_click=self.export_excel,
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )
        
        # ===== دکمه حذف همه داده‌ها =====
        reset_button = ft.ElevatedButton(
            "🗑️ حذف همه داده‌ها",
            on_click=self.reset_all_data,
            bgcolor=ft.Colors.RED_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )
        
        self.content = ft.Column([
            ft.Text("⚙️ تنظیمات", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            ft.Divider(color=ft.Colors.BLUE_200),
            
            # ظاهر
            ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Text("🎨 ظاهر", size=18, weight=ft.FontWeight.BOLD),
                        self.theme_toggle,
                    ]),
                    padding=15
                )
            ),
            
            # پومودورو
            ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Text("🍅 تنظیمات پومودورو", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Text("تمرکز:"),
                            self.work_input,
                            ft.Text("دقیقه"),
                            ft.Text("استراحت:"),
                            self.break_input,
                            ft.Text("دقیقه"),
                            ft.Text("استراحت طولانی:"),
                            self.long_break_input,
                            ft.Text("دقیقه"),
                        ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ]),
                    padding=15
                )
            ),
            
            # خروجی Excel
            ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Text("📊 خروجی داده‌ها", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([export_excel_button], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Text("خروجی Excel شامل تمام کارها با جزئیات کامل", size=12, color=ft.Colors.GREY_500),
                    ]),
                    padding=15
                )
            ),
            
            # حذف داده‌ها
            ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Text("⚠️ خطرناک", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700),
                        ft.Text("حذف همه داده‌ها غیرقابل بازگشت است!", size=14, color=ft.Colors.RED_400),
                        ft.Text("🗑️ همه کارها, عادت‌ها, اهداف, تاریخچه و امتیازات", size=12, color=ft.Colors.GREY_600),
                        reset_button,
                    ]),
                    padding=15
                )
            ),
            
            # درباره
            ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Text("ℹ️ درباره", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("مدیر زمان هوشمند v2.0", size=14),
                        ft.Text("ساخته شده با ❤️ و Flet", size=12, color=ft.Colors.GREY_600),
                        ft.Text("📞 09144505163", size=12, color=ft.Colors.BLUE_700),
                    ]),
                    padding=15
                )
            ),
        ], scroll=ft.ScrollMode.AUTO)
    
    def toggle_theme(self, e):
        theme = 'dark' if e.control.value else 'light'
        self.db.execute('UPDATE settings SET theme = ?', (theme,))
        
        if e.control.value:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.page.bgcolor = ft.Colors.GREY_900
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.page.bgcolor = ft.Colors.GREY_50
        self.page.update()
    
    def update_settings(self, e):
        try:
            work = int(self.work_input.value) if self.work_input.value else 25
            break_time = int(self.break_input.value) if self.break_input.value else 5
            long_break = int(self.long_break_input.value) if self.long_break_input.value else 15
            
            self.db.execute(
                'UPDATE settings SET pomodoro_work = ?, pomodoro_break = ?, pomodoro_long_break = ?',
                (work, break_time, long_break)
            )
            self._show_message("✅ تنظیمات ذخیره شد!", ft.Colors.GREEN_700)
        except:
            self._show_message("⚠️ مقدار عددی وارد کن!", ft.Colors.RED_400)
    
    # ===== خروجی Excel =====
    def export_excel(self, e):
        try:
            filename = f"گزارش_مدیریت_زمان_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            tasks = self._get_all_data()
            
            if not tasks:
                self._show_message("📭 هیچ داده‌ای برای خروجی وجود ندارد!", ft.Colors.ORANGE_700)
                return
            
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=tasks[0].keys())
                writer.writeheader()
                writer.writerows(tasks)
            
            self._show_message(f"✅ خروجی Excel ذخیره شد: {filename}", ft.Colors.GREEN_700)
        except Exception as err:
            self._show_message(f"❌ خطا: {str(err)}", ft.Colors.RED_400)
    
    def _get_all_data(self):
        data = []
        
        self.db.cursor.execute('''
            SELECT id, title, category, priority, done, deadline, created_at, notes 
            FROM tasks ORDER BY id
        ''')
        rows = self.db.cursor.fetchall()
        
        for row in rows:
            deadline_display = row[5] or 'بدون تاریخ'
            if row[5]:
                try:
                    miladi = datetime.strptime(row[5], "%Y-%m-%d")
                    jalali = jdatetime.date.fromgregorian(date=miladi)
                    deadline_display = jalali.strftime("%Y/%m/%d")
                except:
                    deadline_display = row[5]
            
            data.append({
                'شماره': row[0],
                'عنوان': row[1],
                'دسته‌بندی': row[2] or 'سایر',
                'اولویت': row[3] or 'متوسط',
                'وضعیت': 'انجام شده' if row[4] else 'در انتظار',
                'تاریخ سررسید': deadline_display,
                'تاریخ ایجاد': row[6][:10] if row[6] else '',
                'یادداشت': row[7] or ''
            })
        
        return data
    
    # ===== حذف کامل داده‌ها (نسخه نهایی با لاگ کامل) =====
    def reset_all_data(self, e):
        def confirm_reset():
            try:
                print("========== RESET START ==========")

                # حذف اطلاعات وابسته قبل از والد
                delete_tables = [
                    "reminders",
                    "habit_logs",
                    "goal_steps",
                    "pomodoro_sessions",
                    "focus_sessions",
                    "daily_energy",
                    "tasks",
                    "habits",
                    "goals",
                ]

                for table in delete_tables:
                    try:
                        self.db.execute(f"DELETE FROM {table}")
                        print(f"OK: {table}")
                    except Exception as err:
                        print(f"SKIP {table}: {err}")

                # صفر کردن گیمیفیکیشن
                self.db.execute("""
                    UPDATE gamification
                    SET points = 0,
                        level = 1,
                        streak = 0,
                        badges = '[]',
                        total_focus_time = 0
                """)
                print("OK: gamification")

                # بازگرداندن تنظیمات
                self.db.execute("""
                    UPDATE settings
                    SET theme = 'light',
                        language = 'fa',
                        pomodoro_work = 25,
                        pomodoro_break = 5,
                        pomodoro_long_break = 15,
                        sound_enabled = 1,
                        notifications_enabled = 1
                """)
                print("OK: settings")

                # اطمینان از ذخیره شدن
                self.db.conn.commit()

                # بارگذاری مجدد Managerها
                if self.task_manager is not None:
                    self.task_manager.load()
                    print("OK: task_manager reloaded")

                if self.habit_manager is not None:
                    self.habit_manager.load()
                    print("OK: habit_manager reloaded")

                if self.goal_manager is not None:
                    self.goal_manager.load()
                    print("OK: goal_manager reloaded")

                if self.gamification is not None:
                    self.gamification.load()
                    print("OK: gamification reloaded")

                # بستن دیالوگ
                self.close_dialog()

                # به‌روزرسانی صفحه
                self.page.controls.clear()
                self.build()

                self._show_message(
                    "✅ تمام اطلاعات با موفقیت حذف شد.",
                    ft.Colors.GREEN_700
                )

                print("========== RESET COMPLETE ==========")

            except Exception as err:
                print("========== RESET ERROR ==========")
                print(repr(err))
                print("=================================")

                try:
                    self.close_dialog()
                except:
                    pass

                self._show_message(
                    f"❌ خطا در حذف اطلاعات:\n{err}",
                    ft.Colors.RED_700
                )

        # دیالوگ تأیید
        dialog = ft.AlertDialog(
            title=ft.Text(
                "⚠️ حذف تمام اطلاعات",
                rtl=True,
                color=ft.Colors.RED_700,
                weight=ft.FontWeight.BOLD
            ),
            content=ft.Column([
                ft.Text(
                    "آیا مطمئن هستید؟",
                    rtl=True,
                    size=18,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "تمام اطلاعات زیر حذف خواهد شد:",
                    rtl=True
                ),
                ft.Text("🗑️ کارها", rtl=True),
                ft.Text("🗑️ عادت‌ها و تاریخچه", rtl=True),
                ft.Text("🗑️ اهداف و مراحل", rtl=True),
                ft.Text("🗑️ جلسات پومودورو", rtl=True),
                ft.Text("🗑️ جلسات تمرکز", rtl=True),
                ft.Text("🗑️ اطلاعات انرژی", rtl=True),
                ft.Text("🗑️ یادآورها", rtl=True),
                ft.Text("🔄 امتیازات به صفر برمی‌گردد", rtl=True),
                ft.Divider(),
                ft.Text(
                    "⚠️ این عملیات قابل بازگشت نیست.",
                    rtl=True,
                    color=ft.Colors.RED_700,
                    weight=ft.FontWeight.BOLD
                ),
            ], tight=True),
            actions=[
                ft.TextButton(
                    "لغو",
                    on_click=lambda _: self.close_dialog()
                ),
                ft.ElevatedButton(
                    "🗑️ حذف همه",
                    on_click=lambda _: confirm_reset(),
                    bgcolor=ft.Colors.RED_700,
                    color=ft.Colors.WHITE
                )
            ]
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def close_dialog(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def _show_message(self, msg, color):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color, duration=3000)
        self.page.snack_bar.open = True
        self.page.update()
