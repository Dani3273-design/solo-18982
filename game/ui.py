import pygame
import sys
import os


class UIConstants:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (64, 64, 64)
    BLUE = (52, 152, 219)
    GREEN = (46, 204, 113)
    RED = (231, 76, 60)
    ORANGE = (243, 156, 18)
    PURPLE = (155, 89, 182)
    BROWN = (139, 69, 19)
    GOLD = (255, 215, 0)
    
    WALL_TOP = (160, 160, 160)
    WALL_FRONT = (100, 100, 100)
    WALL_SIDE = (130, 130, 130)
    FLOOR = (220, 220, 210)


class FontManager:
    def __init__(self):
        self.fonts = {}
        self.default_font = None
        
    def get_font(self, size, bold=False):
        key = (size, bold)
        if key in self.fonts:
            return self.fonts[key]
        
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/HelveticaNeue.ttc",
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = pygame.font.Font(font_path, size)
                    break
                except:
                    continue
        
        if font is None:
            font = pygame.font.SysFont("arial", size, bold)
        
        self.fonts[key] = font
        return font
    
    def render_text(self, text, size, color, bold=False):
        font = self.get_font(size, bold)
        return font.render(text, True, color)


class Button:
    def __init__(self, x, y, width, height, text, font_manager, 
                 bg_color=UIConstants.BLUE, hover_color=UIConstants.GREEN, 
                 text_color=UIConstants.WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_manager = font_manager
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.bg_color
        
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, UIConstants.WHITE, self.rect, 3, border_radius=10)
        
        text_surface = self.font_manager.render_text(self.text, 32, self.text_color, bold=True)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False


class StartScreen:
    def __init__(self, width, height, font_manager):
        self.width = width
        self.height = height
        self.font_manager = font_manager
        
        button_width = 200
        button_height = 60
        button_x = (width - button_width) // 2
        button_y = height - 150
        
        self.start_button = Button(
            button_x, button_y, button_width, button_height,
            "开始游戏", font_manager,
            bg_color=UIConstants.BLUE,
            hover_color=UIConstants.GREEN
        )
    
    def draw(self, surface):
        gradient_surface = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            r = 30 + (y * 20) // self.height
            g = 40 + (y * 30) // self.height
            b = 80 + (y * 40) // self.height
            pygame.draw.line(gradient_surface, (r, g, b), (0, y), (self.width, y))
        surface.blit(gradient_surface, (0, 0))
        
        title_surface = self.font_manager.render_text("3D 迷宫滚球", 72, UIConstants.GOLD, bold=True)
        title_rect = title_surface.get_rect(center=(self.width // 2, 100))
        surface.blit(title_surface, title_rect)
        
        instructions = [
            "游戏说明：",
            "1. 鼠标点击并拖拽来控制迷宫倾斜",
            "2. 小球会随着迷宫倾斜方向滚动",
            "3. 将小球滚入黑色洞口即可通关",
            "4. 注意：松开鼠标后迷宫会缓慢复原",
        ]
        
        left_margin = 180
        y_offset = 200
        for i, line in enumerate(instructions):
            if i == 0:
                color = UIConstants.ORANGE
                size = 36
                bold = True
                text_surface = self.font_manager.render_text(line, size, color, bold)
                text_rect = text_surface.get_rect(center=(self.width // 2, y_offset))
                surface.blit(text_surface, text_rect)
            else:
                color = UIConstants.LIGHT_GRAY
                size = 28
                bold = False
                text_surface = self.font_manager.render_text(line, size, color, bold)
                surface.blit(text_surface, (left_margin, y_offset))
            
            y_offset += 50
        
        self.start_button.draw(surface)
    
    def handle_event(self, event):
        return self.start_button.handle_event(event)


class LoadingScreen:
    def __init__(self, width, height, font_manager):
        self.width = width
        self.height = height
        self.font_manager = font_manager
        self.rotation_angle = 0
        
    def draw(self, surface):
        surface.fill(UIConstants.DARK_GRAY)
        
        loading_text = self.font_manager.render_text("正在生成迷宫...", 48, UIConstants.WHITE, bold=True)
        loading_rect = loading_text.get_rect(center=(self.width // 2, self.height // 2 - 80))
        surface.blit(loading_text, loading_rect)
        
        center_x, center_y = self.width // 2, self.height // 2 + 40
        radius = 50
        
        self.rotation_angle = (self.rotation_angle + 5) % 360
        
        import math
        for i in range(8):
            angle = self.rotation_angle + i * 45
            rad = math.radians(angle)
            x = center_x + math.cos(rad) * radius
            y = center_y + math.sin(rad) * radius
            
            pygame.draw.circle(surface, UIConstants.BLUE, (int(x), int(y)), 12 - i)
            pygame.draw.circle(surface, UIConstants.WHITE, (int(x), int(y)), 12 - i, 2)
        
        tip_text = self.font_manager.render_text("请稍候，迷宫生成中...", 24, UIConstants.LIGHT_GRAY)
        tip_rect = tip_text.get_rect(center=(self.width // 2, self.height - 80))
        surface.blit(tip_text, tip_rect)


class GameScreen:
    def __init__(self, width, height, font_manager):
        self.width = width
        self.height = height
        self.font_manager = font_manager
        
    def draw(self, surface, labyrinth_3d, ball, timer, tilt_x, tilt_y):
        surface.fill((30, 40, 50))
        
        draw_data = labyrinth_3d.get_draw_data()
        
        goal_screen_pos = labyrinth_3d.get_goal_screen_pos()
        
        for item in draw_data:
            if item['type'] == 'floor':
                floor_render = labyrinth_3d.render_floor(item)
                
                gx, gy = item['gx'], item['gy']
                goal_grid_x = int(labyrinth_3d.generator.end_pos[0])
                goal_grid_y = int(labyrinth_3d.generator.end_pos[1])
                
                if gx == goal_grid_x and gy == goal_grid_y:
                    pygame.draw.polygon(surface, floor_render['color'], floor_render['polygon'])
                    center_x = sum(p[0] for p in floor_render['polygon']) / 4
                    center_y = sum(p[1] for p in floor_render['polygon']) / 4
                    pygame.draw.circle(surface, UIConstants.BLACK, (int(center_x), int(center_y)), 14)
                    pygame.draw.circle(surface, UIConstants.ORANGE, (int(center_x), int(center_y)), 17, 2)
                else:
                    pygame.draw.polygon(surface, floor_render['color'], floor_render['polygon'])
                
                pygame.draw.polygon(surface, (170, 170, 160), floor_render['polygon'], 1)
        
        ball_screen_pos = labyrinth_3d.get_ball_screen_pos(ball.x, ball.y)
        ball_depth = ball.y
        
        for item in draw_data:
            if item['type'] == 'wall':
                if item['depth'] > ball_depth:
                    continue
                
                wall_faces = labyrinth_3d.render_wall(item)
                for face in wall_faces:
                    pygame.draw.polygon(surface, face['color'], face['polygon'])
                    pygame.draw.polygon(surface, (50, 50, 50), face['polygon'], 1)
        
        shadow_x = ball_screen_pos[0] + 4
        shadow_y = ball_screen_pos[1] + 4
        pygame.draw.circle(surface, (20, 20, 20), (int(shadow_x), int(shadow_y)), ball.radius)
        
        pygame.draw.circle(surface, UIConstants.RED, (int(ball_screen_pos[0]), int(ball_screen_pos[1])), ball.radius)
        pygame.draw.circle(surface, (180, 30, 30), (int(ball_screen_pos[0]), int(ball_screen_pos[1])), ball.radius, 2)
        
        highlight_x = int(ball_screen_pos[0] - ball.radius // 3)
        highlight_y = int(ball_screen_pos[1] - ball.radius // 3)
        pygame.draw.circle(surface, (255, 150, 150), (highlight_x, highlight_y), ball.radius // 3)
        
        for item in draw_data:
            if item['type'] == 'wall':
                if item['depth'] <= ball_depth:
                    continue
                
                wall_faces = labyrinth_3d.render_wall(item)
                for face in wall_faces:
                    pygame.draw.polygon(surface, face['color'], face['polygon'])
                    pygame.draw.polygon(surface, (50, 50, 50), face['polygon'], 1)
        
        time_text = self.font_manager.render_text(f"时间: {timer.format_time()}", 36, UIConstants.WHITE, bold=True)
        surface.blit(time_text, (20, 20))
        
        tilt_text = self.font_manager.render_text(f"倾斜: X={tilt_x:.1f}° Y={tilt_y:.1f}°", 24, UIConstants.LIGHT_GRAY)
        surface.blit(tilt_text, (20, 60))
        
        instruction_text = self.font_manager.render_text("按住鼠标拖拽控制迷宫", 20, UIConstants.LIGHT_GRAY)
        surface.blit(instruction_text, (self.width - 250, 20))


class EndScreen:
    def __init__(self, width, height, font_manager):
        self.width = width
        self.height = height
        self.font_manager = font_manager
        self.final_time = ""
        
        button_width = 200
        button_height = 60
        button_x = (width - button_width) // 2
        button_y = height - 150
        
        self.restart_button = Button(
            button_x, button_y, button_width, button_height,
            "重新开始", font_manager,
            bg_color=UIConstants.GREEN,
            hover_color=UIConstants.BLUE
        )
    
    def set_final_time(self, time_str):
        self.final_time = time_str
    
    def draw(self, surface):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        congrats_text = self.font_manager.render_text("恭喜通关！", 64, UIConstants.GOLD, bold=True)
        congrats_rect = congrats_text.get_rect(center=(self.width // 2, 150))
        surface.blit(congrats_text, congrats_rect)
        
        time_label = self.font_manager.render_text("通关用时:", 40, UIConstants.WHITE, bold=True)
        time_label_rect = time_label.get_rect(center=(self.width // 2, 280))
        surface.blit(time_label, time_label_rect)
        
        time_text = self.font_manager.render_text(self.final_time, 56, UIConstants.GREEN, bold=True)
        time_rect = time_text.get_rect(center=(self.width // 2, 360))
        surface.blit(time_text, time_rect)
        
        stars = 3
        if self.final_time:
            try:
                parts = self.final_time.split(':')
                if len(parts) == 2:
                    minutes = int(parts[0])
                    seconds = float(parts[1].replace('.', '')) / 100
                    total_seconds = minutes * 60 + seconds
                else:
                    total_seconds = float(self.final_time.replace('.', '')) / 100
                
                if total_seconds < 30:
                    stars = 3
                elif total_seconds < 60:
                    stars = 2
                else:
                    stars = 1
            except:
                stars = 2
        
        star_text = self.font_manager.render_text("★" * stars + "☆" * (3 - stars), 48, UIConstants.GOLD)
        star_rect = star_text.get_rect(center=(self.width // 2, 440))
        surface.blit(star_text, star_rect)
        
        self.restart_button.draw(surface)
    
    def handle_event(self, event):
        return self.restart_button.handle_event(event)
