# pages/calendar.py
import flet as ft
from managers.task_manager import TaskManager
from managers.habit_manager import HabitManager
from managers.goal_manager import GoalManager
from datetime import datetime, timedelta
import jdatetime

class CalendarPage:
    def __init__(self, page: ft.Page, task_manager: TaskManager, habit_manager: HabitManager = None, goal_manager: GoalManager = None, energy_db=None):
        self.page = page
        self.task_manager = task_manager
        self.habit_manager = habit_manager
        self.goal_manager = goal_manager
        self.energy_db = energy_db
        self.current_date = jdatetime.date.today()
        self.selected_date = self.current_date
        
        if self.selected_date is None:
            self.selected_date = self.current_date
        
        self.build()
    
    def build(self):
        # ===== انتخاب سال و ماه =====
        current_year = jdatetime.date.today().year
        years = [str(y) for y in range(current_year - 10, current_year + 11)]
        months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                  'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
        
        self.year_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(year, year) for year in years],
            value=str(self.current_date.year),
            width=120,
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
            on_change=self.on_year_change,
        )
        
        self.month_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(str(i+1), months[i]) for i in range(12)],
            value=str(self.current_date.month),
            width=140,
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
            on_change=self.on_month_change,
        )
        
        self.selector_row = ft.Row([
            ft.Text("📅", size=28),
            self.year_dropdown,
            self.month_dropdown,
            ft.IconButton(
                icon="REFRESH",
                on_click=lambda _: self.go_today(),
                tooltip="برو به امروز",
                icon_color=ft.Colors.BLUE_700,
                icon_size=30,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
        
        # ===== جدول تقویم =====
        weekdays = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
        
        self.header_row = ft.Row(
            [ft.Container(
                content=ft.Text(day, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_700,
                border_radius=8,
                padding=ft.padding.symmetric(vertical=12),
                expand=True,
                alignment=ft.alignment.center,
            ) for day in weekdays],
            spacing=8,
        )
        
        self.days_grid = ft.Column(spacing=8)
        
        # ===== بخش رویدادهای روز =====
        self.events_title = ft.Text("📌 رویدادهای این روز", size=18, weight=ft.FontWeight.BOLD)
        self.events_list = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO)
        
        # ===== آمار ماه =====
        self.task_stat = ft.Text("📋 0", size=14)
        self.goal_stat = ft.Text("🎯 0", size=14)
        self.habit_stat = ft.Text("🔄 0", size=14)
        self.energy_stat = ft.Text("⚡ 0", size=14)
        
        self.month_stats = ft.Container(
            content=ft.Row([
                ft.Container(content=self.task_stat, padding=ft.padding.symmetric(horizontal=12, vertical=6), bgcolor=ft.Colors.GREEN_50, border_radius=8),
                ft.Container(content=self.goal_stat, padding=ft.padding.symmetric(horizontal=12, vertical=6), bgcolor=ft.Colors.PURPLE_50, border_radius=8),
                ft.Container(content=self.habit_stat, padding=ft.padding.symmetric(horizontal=12, vertical=6), bgcolor=ft.Colors.ORANGE_50, border_radius=8),
                ft.Container(content=self.energy_stat, padding=ft.padding.symmetric(horizontal=12, vertical=6), bgcolor=ft.Colors.YELLOW_50, border_radius=8),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
            padding=12,
            bgcolor=ft.Colors.GREY_50,
            border_radius=10,
            margin=ft.margin.only(top=10, bottom=10),
        )
        
        self.content = ft.Column([
            ft.Row([ft.Text("📅 تقویم شمسی", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(color=ft.Colors.BLUE_200),
            self.selector_row,
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            self.header_row,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self.days_grid,
            self.month_stats,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self.events_title,
            ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
            ft.Container(content=self.events_list, height=300, border=ft.border.all(1, ft.Colors.GREY_300), border_radius=10, padding=10),
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.page.add(self.content)
        self.update_calendar()
    
    def on_year_change(self, e):
        new_year = int(self.year_dropdown.value)
        self.current_date = jdatetime.date(new_year, self.current_date.month, 1)
        self.update_calendar()
    
    def on_month_change(self, e):
        new_month = int(self.month_dropdown.value)
        self.current_date = jdatetime.date(self.current_date.year, new_month, 1)
        self.update_calendar()
    
    def go_today(self):
        self.current_date = jdatetime.date.today()
        self.selected_date = self.current_date
        self.year_dropdown.value = str(self.current_date.year)
        self.month_dropdown.value = str(self.current_date.month)
        self.update_calendar()
    
    def _get_energy_for_date(self, date_str):
        """دریافت انرژی برای یک تاریخ میلادی"""
        if not self.energy_db:
            return None
        try:
            self.energy_db.cursor.execute('SELECT energy_level, notes, mood FROM daily_energy WHERE date = ?', (date_str,))
            row = self.energy_db.cursor.fetchone()
            if row:
                return {"level": row[0], "notes": row[1], "mood": row[2]}
            return None
        except Exception as e:
            print(f"خطا در دریافت انرژی: {e}")
            return None
    
    def _get_all_events_for_day(self, date_obj):
        """دریافت همه رویدادهای یک روز"""
        # تاریخ میلادی برای جستجو در دیتابیس
        gregorian_date = date_obj.togregorian().strftime("%Y-%m-%d")
        day_str = date_obj.strftime("%Y-%m-%d")
        
        events = []
        
        # 1. کارها - با تاریخ میلادی
        tasks_all = self.task_manager.get_all() if self.task_manager else []
        day_tasks = [t for t in tasks_all if t.deadline == gregorian_date]
        
        for task in day_tasks:
            events.append({
                "type": "کار",
                "icon": "📋",
                "title": task.title,
                "color": ft.Colors.GREEN_700,
                "status": "✅ انجام شده" if task.done else "⏳ در انتظار",
                "detail": f"اولویت: {task.priority} | دسته: {task.category}"
            })
        
        # 2. عادت‌ها - با تاریخ میلادی
        habits_all = self.habit_manager.get_all() if self.habit_manager else []
        day_habits = [h for h in habits_all if h.last_done == gregorian_date]
        
        for habit in day_habits:
            events.append({
                "type": "عادت",
                "icon": "🔄",
                "title": habit.name,
                "color": ft.Colors.ORANGE_700,
                "status": f"🔥 {habit.streak} روز متوالی",
                "detail": f"بهترین رکورد: {habit.best_streak} روز"
            })
        
        # 3. اهداف - با تاریخ میلادی
        goals_all = self.goal_manager.get_all() if self.goal_manager else []
        day_goals = [g for g in goals_all if g.target_date == gregorian_date]
        
        for goal in day_goals:
            steps = len(goal.steps) if hasattr(goal, 'steps') and goal.steps else 0
            events.append({
                "type": "هدف",
                "icon": "🎯",
                "title": goal.title,
                "color": ft.Colors.PURPLE_700,
                "status": f"{goal.progress}% پیشرفت",
                "detail": f"تاریخ هدف: {goal.target_date} | {steps} مرحله"
            })
        
        # 4. انرژی
        energy_data = self._get_energy_for_date(gregorian_date)
        if energy_data:
            level = energy_data.get("level")
            notes = energy_data.get("notes", "")
            mood = energy_data.get("mood", "")
            
            energy_icon = "⚡" if level == "زیاد" else "🔋" if level == "متوسط" else "🪫"
            events.append({
                "type": "انرژی",
                "icon": energy_icon,
                "title": f"انرژی: {level}",
                "color": ft.Colors.YELLOW_700,
                "status": f"حالت: {mood}" if mood else "ثبت شده",
                "detail": f"یادداشت: {notes}" if notes else "بدون یادداشت"
            })
        
        return events
    
    def update_calendar(self):
        self.days_grid.controls.clear()
        
        first_day = jdatetime.date(self.current_date.year, self.current_date.month, 1)
        first_weekday = first_day.weekday()
        
        # تعداد روزهای ماه
        if self.current_date.month in [1, 2, 3, 4, 5, 6]:
            days_in_month = 31
        elif self.current_date.month in [7, 8, 9, 10, 11]:
            days_in_month = 30
        else:
            days_in_month = 29 if jdatetime.date(self.current_date.year, 12, 29).day == 29 else 30
        
        month_tasks = 0
        month_goals = 0
        month_habits = 0
        month_energy = 0
        
        week_rows = []
        current_row = []
        
        # روزهای خالی ابتدای ماه
        for _ in range(first_weekday):
            current_row.append(None)
        
        for day in range(1, days_in_month + 1):
            date_obj = jdatetime.date(self.current_date.year, self.current_date.month, day)
            
            # دریافت رویدادها
            day_events = self._get_all_events_for_day(date_obj)
            total_events = len(day_events)
            has_events = total_events > 0
            
            is_today = date_obj == jdatetime.date.today()
            is_selected = date_obj == self.selected_date
            
            # آمار ماه
            gregorian_date = date_obj.togregorian().strftime("%Y-%m-%d")
            
            tasks_all = self.task_manager.get_all() if self.task_manager else []
            month_tasks += len([t for t in tasks_all if t.deadline == gregorian_date])
            
            goals_all = self.goal_manager.get_all() if self.goal_manager else []
            month_goals += len([g for g in goals_all if g.target_date == gregorian_date])
            
            habits_all = self.habit_manager.get_all() if self.habit_manager else []
            month_habits += 1 if [h for h in habits_all if h.last_done == gregorian_date] else 0
            
            month_energy += 1 if self._get_energy_for_date(gregorian_date) else 0
            
            current_row.append((day, date_obj, day_events, is_today, is_selected, has_events, total_events))
            
            if len(current_row) == 7:
                week_rows.append(current_row)
                current_row = []
        
        # روزهای خالی انتهای ماه
        while len(current_row) < 7 and current_row:
            current_row.append(None)
        if current_row:
            week_rows.append(current_row)
        
        # ساخت نمایش گرید
        for week in week_rows:
            week_row = ft.Row(spacing=8)
            for item in week:
                if item is None:
                    week_row.controls.append(
                        ft.Container(
                            expand=True,
                            height=100,
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=10,
                        )
                    )
                else:
                    day, date_obj, day_events, is_today, is_selected, has_events, total_events = item
                    
                    # تعیین رنگ پس‌زمینه
                    if is_selected:
                        bg_color = ft.Colors.BLUE_700
                        text_color = ft.Colors.WHITE
                        border_color = ft.Colors.BLUE_900
                    elif is_today:
                        bg_color = ft.Colors.BLUE_100
                        text_color = ft.Colors.BLACK
                        border_color = ft.Colors.BLUE_400
                    elif day_events:
                        bg_color = ft.Colors.GREEN_50
                        text_color = ft.Colors.BLACK
                        border_color = ft.Colors.GREEN_300
                    else:
                        bg_color = ft.Colors.WHITE
                        text_color = ft.Colors.BLACK
                        border_color = ft.Colors.GREY_300
                    
                    # آیکون‌های رویدادها
                    event_icons = ft.Row(spacing=2, alignment=ft.MainAxisAlignment.CENTER)
                    for event in day_events[:4]:
                        event_icons.controls.append(ft.Text(event["icon"], size=14))
                    
                    # ساخت کارت روز
                    day_card = ft.Container(
                        content=ft.Column([
                            ft.Text(
                                str(day),
                                size=24,
                                weight=ft.FontWeight.BOLD if is_today or is_selected else ft.FontWeight.NORMAL,
                                color=text_color,
                            ),
                            event_icons,
                            ft.Text(
                                f"{total_events} رویداد" if has_events else "",
                                size=10,
                                color=ft.Colors.GREY_500 if not is_selected else ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                        expand=True,
                        height=100,
                        alignment=ft.alignment.center,
                        bgcolor=bg_color,
                        border_radius=10,
                        border=ft.border.all(2, border_color),
                        on_click=lambda e, d=date_obj: self.select_date(d),
                        tooltip=self._get_tooltip(day_events),
                    )
                    week_row.controls.append(day_card)
            
            self.days_grid.controls.append(week_row)
        
        # به‌روزرسانی آمار
        self.task_stat.value = f"📋 {month_tasks}"
        self.goal_stat.value = f"🎯 {month_goals}"
        self.habit_stat.value = f"🔄 {month_habits}"
        self.energy_stat.value = f"⚡ {month_energy}"
        for stat in [self.task_stat, self.goal_stat, self.habit_stat, self.energy_stat]:
            stat.update()
        
        self.show_events_for_day()
        self.page.update()
    
    def _get_tooltip(self, events):
        if not events:
            return ""
        tooltip = []
        for event in events:
            tooltip.append(f"{event['icon']} {event['title']}")
        return "\n".join(tooltip)
    
    def select_date(self, date_obj):
        self.selected_date = date_obj
        self.update_calendar()
    
    def show_events_for_day(self):
        """نمایش رویدادهای روز انتخاب شده"""
        self.events_list.controls.clear()
        
        if self.selected_date is None:
            self.selected_date = jdatetime.date.today()
        
        day_events = self._get_all_events_for_day(self.selected_date)
        date_display = self.selected_date.strftime("%Y/%m/%d")
        
        self.events_title.value = f"📌 رویدادهای {date_display}"
        
        if not day_events:
            self.events_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name="CALENDAR_TODAY", size=40, color=ft.Colors.GREY_300),
                        ft.Text("هیچ رویدادی در این روز نیست!", size=14, color=ft.Colors.GREY_500),
                        ft.Text("برای افزودن به بخش مربوطه بروید", size=12, color=ft.Colors.GREY_400),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30,
                )
            )
        else:
            # مرتب‌سازی بر اساس نوع
            type_order = {"کار": 0, "هدف": 1, "عادت": 2, "انرژی": 3}
            day_events.sort(key=lambda x: type_order.get(x["type"], 99))
            
            for event in day_events:
                self.events_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(event["icon"], size=24),
                                    ft.Column([
                                        ft.Text(event["title"], size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(event["status"], size=13, color=ft.Colors.GREY_600),
                                        ft.Text(event.get("detail", ""), size=11, color=ft.Colors.GREY_500),
                                    ], spacing=2, expand=True),
                                    ft.Container(
                                        content=ft.Text(event["type"], size=10, color=ft.Colors.WHITE),
                                        bgcolor=event["color"],
                                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                        border_radius=5,
                                    ),
                                ]),
                            ]),
                            padding=12,
                        ),
                        elevation=2,
                        margin=ft.margin.only(bottom=5),
                    )
                )
        
        self.page.update()
