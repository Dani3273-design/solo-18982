import pygame
import threading


class MouseController:
    def __init__(self, max_tilt=15):
        self.max_tilt = max_tilt
        self.tilt_x = 0
        self.tilt_y = 0
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.sensitivity = 0.3
        self.return_speed = 0.1
        self.lock = threading.Lock()
        
    def handle_event(self, event):
        with self.lock:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.is_dragging = True
                    self.drag_start_x = event.pos[0]
                    self.drag_start_y = event.pos[1]
                    self.last_mouse_x = event.pos[0]
                    self.last_mouse_y = event.pos[1]
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    dx = event.pos[0] - self.last_mouse_x
                    dy = event.pos[1] - self.last_mouse_y
                    
                    self.tilt_x += dx * self.sensitivity
                    self.tilt_y += dy * self.sensitivity
                    
                    self.tilt_x = max(-self.max_tilt, min(self.max_tilt, self.tilt_x))
                    self.tilt_y = max(-self.max_tilt, min(self.max_tilt, self.tilt_y))
                    
                    self.last_mouse_x = event.pos[0]
                    self.last_mouse_y = event.pos[1]
    
    def update(self):
        with self.lock:
            if not self.is_dragging:
                if abs(self.tilt_x) > 0.1:
                    self.tilt_x *= (1 - self.return_speed)
                else:
                    self.tilt_x = 0
                
                if abs(self.tilt_y) > 0.1:
                    self.tilt_y *= (1 - self.return_speed)
                else:
                    self.tilt_y = 0
    
    def get_tilt(self):
        with self.lock:
            return self.tilt_x, self.tilt_y
    
    def reset(self):
        with self.lock:
            self.tilt_x = 0
            self.tilt_y = 0
            self.is_dragging = False
