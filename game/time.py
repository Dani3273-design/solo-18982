import time
import threading


class GameTimer:
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0
        self.is_running = False
        self.pause_time = 0
        self.lock = threading.Lock()
        
    def start(self):
        with self.lock:
            self.start_time = time.time()
            self.elapsed_time = 0
            self.is_running = True
    
    def pause(self):
        with self.lock:
            if self.is_running:
                self.pause_time = time.time()
                self.is_running = False
    
    def resume(self):
        with self.lock:
            if not self.is_running and self.pause_time:
                pause_duration = time.time() - self.pause_time
                if self.start_time:
                    self.start_time += pause_duration
                self.is_running = True
    
    def stop(self):
        with self.lock:
            if self.is_running and self.start_time:
                self.elapsed_time = time.time() - self.start_time
            self.is_running = False
    
    def get_elapsed(self):
        with self.lock:
            if self.is_running and self.start_time:
                return time.time() - self.start_time
            return self.elapsed_time
    
    def format_time(self, seconds=None):
        if seconds is None:
            seconds = self.get_elapsed()
        
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds * 100) % 100)
        
        if minutes > 0:
            return f"{minutes:02d}:{secs:02d}.{milliseconds:02d}"
        else:
            return f"{secs:02d}.{milliseconds:02d}"
    
    def reset(self):
        with self.lock:
            self.start_time = None
            self.elapsed_time = 0
            self.is_running = False
            self.pause_time = 0
