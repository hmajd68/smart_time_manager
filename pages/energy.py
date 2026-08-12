# pages/energy.py
import flet as ft
from database.database import Database
from datetime import datetime
import jdatetime

class EnergyPage:
    def __init__(self, page: ft.Page, db: Database):
        self.page = page
        self.db = db
        self.build()
    
    def build(self):
        today = datetime.now().strftime("%Y-%m-%d")
        jalali_today = jdatetime.date.today().strftime("%Y/%m/%d")
        
        # دریافت اطلاعات امروز
        self.db.cursor.execute('SELECT energy_level, mood, notes FROM daily_energy WHERE date = ?', (today,))
        row = self.db.cursor.fetchone()
        
        current_energy = row[0] if row else None
        current_mood = row[1] if row else ""
        current_notes = row[2] if row else ""
        
        # نمایش انرژی فعلی
        self.energy_display = ft.Container(
            content=ft.Row([
                ft.Text("🔋", size=30),
                ft.Text(
                    current_energy if current_energy else "ثبت نشده",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=self._get_energy_color(current_energy),
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=15,
            bgcolor=ft.Colors.GREY_50,
            border_radius=10,
            margin=ft.margin.only(bottom=15),
        )
        
        # دکمه‌های انتخاب انرژی
        energy_buttons = ft.Row([
            self._energy_button("⚡ زیاد", "زیاد", ft.Colors.GREEN_700),
            self._energy_button("🔋 متوسط", "متوسط", ft.Colors.ORANGE_700),
            self._energy_button("🪫 کم", "کم", ft.Colors.RED_700),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
        
        # انتخاب حالت روحی
        self.mood_input = ft.Dropdown(
            options=[
                ft.dropdown.Option("😊 عالی", "عالی"),
                ft.dropdown.Option("🙂 خوب", "خوب"),
                ft.dropdown.Option("😐 متوسط", "متوسط"),
                ft.dropdown.Option("😔 خسته", "خسته"),
                ft.dropdown.Option("😢 بد", "بد"),
            ],
            value=current_mood if current_mood else None,
            hint_text="حال خودت رو انتخاب کن...",
            width=250,
            border_color=ft.Colors.PURPLE_400,
            on_change=self.save_mood,
        )
        
        # 📝 یادداشت روزانه (مثل بخش کارها)
        self.notes_input = ft.TextField(
            hint_text="یادداشت امروز را بنویس...",
            value=current_notes,
            multiline=True,
            max_lines=4,
            width=350,
            border_color=ft.Colors.PURPLE_400,
            focused_border_color=ft.Colors.PURPLE_700,
            on_submit=lambda _: self.save_notes(None),  # با Enter هم ذخیره شود
        )
        
        # دکمه ذخیره یادداشت (مثل دکمه افزودن کارها)
        self.save_notes_btn = ft.ElevatedButton(
            "💾 ذخیره یادداشت",
            on_click=self.save_notes,
            bgcolor=ft.Colors.PURPLE_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )
        
        # لیست یادداشت‌های قبلی (برای نمایش مانند کارها)
        self.notes_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        
        self.content = ft.Column([
            ft.Row([
                ft.Text("⚡ انرژی روزانه", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(color=ft.Colors.PURPLE_200),
            
            ft.Text(f"📅 {jalali_today}", size=16, color=ft.Colors.GREY_600),
            
            self.energy_display,
            
            ft.Text("انرژی امروز خود را انتخاب کن:", size=16, weight=ft.FontWeight.BOLD),
            energy_buttons,
            
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            
            ft.Text("😊 حالت روحی:", size=16, weight=ft.FontWeight.BOLD),
            self.mood_input,
            
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            
            ft.Text("📝 یادداشت روزانه:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                self.notes_input,
                self.save_notes_btn,
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
            
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            
            ft.Text("📋 یادداشت‌های قبلی:", size=18, weight=ft.FontWeight.BOLD),
            self.notes_list,
            
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.page.add(self.content)
        self.load_notes()
        self.page.update()
    
    def load_notes(self):
        """بارگذاری یادداشت‌های قبلی (مثل لیست کارها)"""
        self.notes_list.controls.clear()
        
        # دریافت ۱۰ یادداشت آخر
        self.db.cursor.execute('''
            SELECT date, notes, energy_level, mood 
            FROM daily_energy 
            WHERE notes IS NOT NULL AND notes != '' 
            ORDER BY date DESC 
            LIMIT 10
        ''')
        rows = self.db.cursor.fetchall()
        
        if not rows:
            self.notes_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name="EDIT_NOTE", size=50, color=ft.Colors.GREY_300),
                        ft.Text("هیچ یادداشتی ثبت نشده!", size=16, color=ft.Colors.GREY_500),
                        ft.Text("یک یادداشت جدید بنویس", size=12, color=ft.Colors.GREY_400),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30,
                )
            )
        else:
            for row in rows:
                self.notes_list.controls.append(self._make_note_card(row))
        
        self.page.update()
    
    def _make_note_card(self, row):
        """ساخت کارت یادداشت (مثل کارت کارها)"""
        date = row[0]
        notes = row[1]
        energy = row[2] or "متوسط"
        mood = row[3] or ""
        
        # تبدیل تاریخ میلادی به شمسی
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            jalali_date = jdatetime.date.fromgregorian(date=date_obj)
            date_str = jalali_date.strftime("%Y/%m/%d")
        except:
            date_str = date
        
        energy_icon = "⚡" if energy == "زیاد" else "🔋" if energy == "متوسط" else "🪫"
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(energy_icon, size=16),
                        ft.Text(
                            notes[:50] + ("..." if len(notes) > 50 else ""),
                            size=15,
                            expand=True,
                        ),
                    ]),
                    ft.Row([
                        ft.Text(f"📅 {date_str}", size=12, color=ft.Colors.GREY_500),
                        ft.Text(mood, size=12, color=ft.Colors.GREY_500) if mood else ft.Container(),
                        ft.Text(f"انرژی: {energy}", size=12, color=ft.Colors.GREY_500),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ]),
                padding=12,
            ),
            elevation=2,
            margin=ft.margin.only(bottom=5),
        )
    
    def _energy_button(self, label, level, color):
        return ft.Container(
            content=ft.Text(label, size=16, color=ft.Colors.WHITE),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor=color,
            border_radius=10,
            on_click=lambda e, l=level: self.set_energy(l),
        )
    
    def _get_energy_color(self, level):
        if level == "زیاد":
            return ft.Colors.GREEN_700
        elif level == "متوسط":
            return ft.Colors.ORANGE_700
        elif level == "کم":
            return ft.Colors.RED_700
        return ft.Colors.GREY_500
    
    def set_energy(self, level):
        today = datetime.now().strftime("%Y-%m-%d")
        
        # دریافت یادداشت موجود
        self.db.cursor.execute('SELECT notes, mood FROM daily_energy WHERE date = ?', (today,))
        row = self.db.cursor.fetchone()
        notes = row[0] if row else ""
        mood = row[1] if row else ""
        
        self.db.execute(
            'INSERT OR REPLACE INTO daily_energy (date, energy_level, mood, notes) VALUES (?, ?, ?, ?)',
            (today, level, mood, notes)
        )
        
        # به‌روزرسانی نمایش
        self.energy_display.content.controls[1].value = level
        self.energy_display.content.controls[1].color = self._get_energy_color(level)
        self.energy_display.update()
        
        self.load_notes()
        self._show_message(f"✅ انرژی {level} ثبت شد!", ft.Colors.GREEN_700)
    
    def save_mood(self, e):
        today = datetime.now().strftime("%Y-%m-%d")
        mood = self.mood_input.value
        
        if mood:
            # دریافت اطلاعات موجود
            self.db.cursor.execute('SELECT energy_level, notes FROM daily_energy WHERE date = ?', (today,))
            row = self.db.cursor.fetchone()
            energy = row[0] if row else "متوسط"
            notes = row[1] if row else ""
            
            self.db.execute(
                'INSERT OR REPLACE INTO daily_energy (date, energy_level, mood, notes) VALUES (?, ?, ?, ?)',
                (today, energy, mood, notes)
            )
            self.load_notes()
            self._show_message("✅ حالت روحی ثبت شد!", ft.Colors.GREEN_700)
    
    def save_notes(self, e):
        """ذخیره یادداشت (مثل افزودن کار)"""
        notes = self.notes_input.value or ""
        
        if not notes.strip():
            self._show_message("⚠️ لطفاً یادداشت را بنویس!", ft.Colors.RED_400)
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # دریافت اطلاعات موجود
        self.db.cursor.execute('SELECT energy_level, mood FROM daily_energy WHERE date = ?', (today,))
        row = self.db.cursor.fetchone()
        energy = row[0] if row else "متوسط"
        mood = row[1] if row else ""
        
        self.db.execute(
            'INSERT OR REPLACE INTO daily_energy (date, energy_level, mood, notes) VALUES (?, ?, ?, ?)',
            (today, energy, mood, notes)
        )
        
        # پاک کردن فیلد (مثل کارها)
        self.notes_input.value = ""
        self.notes_input.update()
        
        # به‌روزرسانی لیست
        self.load_notes()
        
        self._show_message("✅ یادداشت ذخیره شد!", ft.Colors.GREEN_700)
    
    def _show_message(self, msg, color):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color, duration=2000)
        self.page.snack_bar.open = True
        self.page.update()
