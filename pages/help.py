# pages/help.py
import flet as ft

class HelpPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.build()
    
    def build(self):
        # اطلاعات توسعه‌دهنده
        developer_info = ft.Container(
            content=ft.Column([
                ft.Text("👨‍💻 توسعه‌دهنده", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.PINK_700),
                ft.Text("حافظ مجد", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Icon(name="PHONE", color=ft.Colors.BLUE_700, size=20),
                    ft.Text("09144505163", size=16, color=ft.Colors.BLUE_700),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([
                    ft.Icon(name="EMAIL", color=ft.Colors.GREY_700, size=20),
                    ft.Text("hafez.majd@gmail.com", size=14, color=ft.Colors.GREY_700),
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=ft.Colors.PINK_50,
            border_radius=15,
            margin=ft.margin.only(bottom=20),
        )
        
        # راهنمای بخش‌ها
        guide_sections = ft.Column([
            self._make_section(
                "📊 داشبورد",
                [
                    "• نمایش آمار کلی کارها",
                    "• تعداد کارهای انجام شده و باقی‌مانده",
                    "• نمایش امتیاز و سطح کاربر",
                ],
                ft.Colors.BLUE_100
            ),
            self._make_section(
                "📋 مدیریت کارها",
                [
                    "• افزودن کار جدید با وارد کردن عنوان و کلیک روی دکمه ➕",
                    "• علامت زدن کار انجام شده با کلیک روی ✔️",
                    "• حذف کار با کلیک روی 🗑️",
                    "• هر کار جدید +۵ امتیاز",
                    "• هر کار انجام شده +۱۰ امتیاز",
                ],
                ft.Colors.PINK_100
            ),
            self._make_section(
                "📅 تقویم شمسی",
                [
                    "• مشاهده تاریخ شمسی",
                    "• مشاهده کارهای هر روز",
                ],
                ft.Colors.GREEN_100
            ),
            self._make_section(
                "📊 ماتریس آیزنهاور",
                [
                    "• دسته‌بندی کارها بر اساس اولویت و فوریت",
                    "• 🔴 مهم و فوری: انجام بده",
                    "• 🟡 مهم و غیر فوری: برنامه‌ریزی کن",
                    "• 🟠 غیر مهم و فوری: واگذار کن",
                    "• ⚪ غیر مهم و غیر فوری: حذف کن",
                ],
                ft.Colors.ORANGE_100
            ),
            self._make_section(
                "🍅 تایمر پومودورو",
                [
                    "• ۲۵ دقیقه تمرکز + ۵ دقیقه استراحت",
                    "• بعد از ۴ جلسه، ۱۵ دقیقه استراحت طولانی",
                    "• هر جلسه کامل +۱۰ امتیاز",
                ],
                ft.Colors.RED_100
            ),
            self._make_section(
                "🔄 مدیریت عادت‌ها",
                [
                    "• افزودن عادت جدید",
                    "• ثبت انجام عادت روزانه",
                    "• هر عادت جدید +۱۰ امتیاز",
                    "• هر ثبت عادت +۵ امتیاز",
                ],
                ft.Colors.PURPLE_100
            ),
            self._make_section(
                "🎯 مدیریت اهداف",
                [
                    "• تعریف هدف جدید",
                    "• تنظیم پیشرفت هدف",
                    "• تکمیل هدف +۲۰ امتیاز",
                ],
                ft.Colors.YELLOW_100
            ),
            self._make_section(
                "🎯 حالت تمرکز",
                [
                    "• شروع و توقف تمرکز",
                    "• هر ۵ دقیقه تمرکز +۵ امتیاز",
                ],
                ft.Colors.INDIGO_100
            ),
            self._make_section(
                "⚡ انرژی روزانه",
                [
                    "• ثبت انرژی روزانه (زیاد، متوسط، کم)",
                    "• ثبت حالت روحی",
                ],
                ft.Colors.TEAL_100
            ),
            self._make_section(
                "📊 گزارش عملکرد",
                [
                    "• گزارش روزانه",
                    "• گزارش هفتگی",
                    "• گزارش ماهانه",
                ],
                ft.Colors.CYAN_100
            ),
            self._make_section(
                "⚙️ تنظیمات",
                [
                    "• تغییر تم (روشن/تاریک)",
                    "• تنظیم زمان پومودورو",
                    "• پشتیبان‌گیری و بازیابی",
                ],
                ft.Colors.GREY_200
            ),
            self._make_section(
                "⭐ سیستم امتیازدهی",
                [
                    "• افزودن کار جدید: +۵ امتیاز",
                    "• انجام کار: +۱۰ امتیاز",
                    "• هر جلسه پومودورو: +۱۰ امتیاز",
                    "• ایجاد عادت جدید: +۱۰ امتیاز",
                    "• ثبت عادت روزانه: +۵ امتیاز",
                    "• هر ۵ دقیقه تمرکز: +۵ امتیاز",
                    "• تکمیل هدف: +۲۰ امتیاز",
                    "• هر ۱۰۰ امتیاز: یک سطح بالاتر",
                ],
                ft.Colors.AMBER_100
            ),
        ], spacing=15)
        
        self.content = ft.Column([
            ft.Text("📖 راهنمای کامل برنامه", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.PINK_700),
            ft.Divider(color=ft.Colors.PINK_200),
            developer_info,
            ft.Text("📚 راهنمای بخش‌ها", size=22, weight=ft.FontWeight.BOLD),
            guide_sections,
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.page.add(self.content)
    
    def _make_section(self, title, items, color):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                    ft.Column([ft.Text(item, size=14) for item in items], spacing=3),
                ]),
                padding=15,
                bgcolor=color,
                border_radius=10,
            ),
            elevation=2,
        )
