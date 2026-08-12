# managers/pomodoro_manager.py
from database.database import Database
from datetime import datetime
import threading
import time

class PomodoroManager:
    def __init__(self, db: Database, work_time=25, break_time=5, long_break=15):
        self.db = db
        self.work_time = work_time * 60
        self.break_time = break_time * 60
        self.long_break = long_break * 60
        self.is_running = False
        self.is_paused = False
        self.is_work = True
        self.remaining = self.work_time
        self.sessions = 0
        self.total_sessions = 0
        self.thread = None
        self.callback = None
        self.on_tick = None
        self.on_complete = None
        self.on_state_change = None
    
    def start(self, callback=None, on_tick=None, on_complete=None, on_state_change=None):
        if not self.is_running and not self.is_paused:
            self.is_running = True
            self.is_paused = False
            self.callback = callback
            self.on_tick = on_tick
            self.on_complete = on_complete
            self.on_state_change = on_state_change
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
    
    def pause(self):
        if self.is_running:
            self.is_running = False
            self.is_paused = True
            if self.on_state_change:
                self.on_state_change('paused', self.remaining)
    
    def resume(self):
        if not self.is_running and self.is_paused and self.remaining > 0:
            self.is_running = True
            self.is_paused = False
            if self.on_state_change:
                self.on_state_change('resumed', self.remaining)
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
    
    def stop(self):
        self.is_running = False
        self.is_paused = False
        if self.on_state_change:
            self.on_state_change('stopped', self.remaining)
    
    def reset(self):
        self.stop()
        self.is_work = True
        self.remaining = self.work_time
        self.sessions = 0
        if self.callback:
            self.callback()
        if self.on_state_change:
            self.on_state_change('reset', self.remaining)
    
    def _run(self):
        while self.is_running and self.remaining > 0:
            time.sleep(1)
            self.remaining -= 1
            if self.on_tick:
                self.on_tick(self.remaining, self.is_work)
        
        if self.remaining == 0 and self.is_running:
            self.sessions += 1
            self.total_sessions += 1
            self.save_session()
            self.switch_mode()
    
    def switch_mode(self):
        self.is_work = not self.is_work
        if self.is_work:
            self.remaining = self.work_time
            message = "تمرکز"
        else:
            if self.sessions % 4 == 0:
                self.remaining = self.long_break
                message = "استراحت طولانی"
            else:
                self.remaining = self.break_time
                message = "استراحت کوتاه"
        
        if self.on_complete:
            self.on_complete(self.is_work, self.remaining, message)
        
        self.start()
    
    def save_session(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.db.cursor.execute(
            'SELECT sessions, total_time FROM pomodoro_sessions WHERE session_date LIKE ?',
            (today + '%',)
        )
        row = self.db.cursor.fetchone()
        if row:
            self.db.execute(
                'UPDATE pomodoro_sessions SET sessions=?, total_time=? WHERE id=?',
                (row[0] + 1, row[1] + self.work_time, row[2])
            )
        else:
            self.db.execute(
                'INSERT INTO pomodoro_sessions (session_date, sessions, total_time) VALUES (?, ?, ?)',
                (datetime.now().strftime("%Y-%m-%d %H:%M"), 1, self.work_time)
            )
    
    def get_remaining_time(self):
        minutes = self.remaining // 60
        seconds = self.remaining % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_today_sessions(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.db.cursor.execute(
            'SELECT sessions, total_time FROM pomodoro_sessions WHERE session_date LIKE ?',
            (today + '%',)
        )
        row = self.db.cursor.fetchone()
        return row if row else (0, 0)
    
    def get_total_sessions(self):
        return self.total_sessions
    
    def get_state(self):
        if self.is_running:
            return 'running'
        elif self.is_paused:
            return 'paused'
        else:
            return 'stopped'
