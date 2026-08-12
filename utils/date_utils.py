# utils/date_utils.py
from datetime import datetime, timedelta
import jdatetime

class DateUtils:
    @staticmethod
    def to_jalali(date_str: str = None) -> str:
        """تبدیل تاریخ میلادی به شمسی"""
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                jalali = jdatetime.date.fromgregorian(date=date_obj)
                return jalali.strftime("%Y/%m/%d")
            except:
                pass
        return jdatetime.date.today().strftime("%Y/%m/%d")
    
    @staticmethod
    def from_jalali(jalali_str: str) -> str:
        """تبدیل تاریخ شمسی به میلادی"""
        try:
            jalali = jdatetime.datetime.strptime(jalali_str, "%Y/%m/%d")
            return jalali.togregorian().strftime("%Y-%m-%d")
        except:
            return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def get_today_jalali() -> str:
        return jdatetime.date.today().strftime("%Y/%m/%d")
    
    @staticmethod
    def get_persian_month_name(month: int) -> str:
        months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                  'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
        return months[month - 1] if 1 <= month <= 12 else ""
    
    @staticmethod
    def get_persian_weekday(date_str: str = None) -> str:
        weekdays = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                jalali = jdatetime.date.fromgregorian(date=date_obj)
                return weekdays[jalali.weekday()]
            except:
                pass
        return weekdays[jdatetime.date.today().weekday()]
    
    @staticmethod
    def get_jalali_months():
        return ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
