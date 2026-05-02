import pygame
import sys
import threading
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.labyrinth import LabyrinthGenerator, Labyrinth3D
from game.ball import Ball
from game.control import MouseController
from game.time import GameTimer
from game.ui import (
    UIConstants, FontManager, StartScreen, LoadingScreen, 
    GameScreen, EndScreen
)


class GameState:
    START = "start"
    LOADING = "loading"
    PLAYING = "playing"
    END = "end"


class Game:
    def __init__(self, width=800, height=600):
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("3D 迷宫滚球")
        
        self.clock = pygame.time.Clock()
        self.font_manager = FontManager()
        
        self.start_screen = StartScreen(width, height, self.font_manager)
        self.loading_screen = LoadingScreen(width, height, self.font_manager)
        self.game_screen = GameScreen(width, height, self.font_manager)
        self.end_screen = EndScreen(width, height, self.font_manager)
        
        self.state = GameState.START
        self.generator = None
        self.labyrinth_3d = None
        self.ball = None
        self.controller = None
        self.timer = GameTimer()
        
        self.generation_thread = None
        self.generation_complete = False
        self.lock = threading.Lock()
        
    def generate_labyrinth_thread(self):
        try:
            self.generator = LabyrinthGenerator(width=11, height=11)
            self.generator.generate()
            
            self.labyrinth_3d = Labyrinth3D(self.generator, self.width, self.height)
            
            start_pos = self.generator.get_start_position()
            self.ball = Ball(start_pos[0], start_pos[1])
            
            self.controller = MouseController(max_tilt=20)
            
            with self.lock:
                self.generation_complete = True
        except Exception as e:
            print(f"迷宫生成错误: {e}")
            import traceback
            traceback.print_exc()
            with self.lock:
                self.generation_complete = True
    
    def start_new_game(self):
        self.state = GameState.LOADING
        self.generation_complete = False
        
        self.generation_thread = threading.Thread(target=self.generate_labyrinth_thread)
        self.generation_thread.daemon = True
        self.generation_thread.start()
        
        self.timer.reset()
    
    def check_generation_complete(self):
        with self.lock:
            if self.generation_complete:
                self.state = GameState.PLAYING
                self.timer.start()
                return True
        return False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if self.state == GameState.START:
                if self.start_screen.handle_event(event):
                    self.start_new_game()
            
            elif self.state == GameState.PLAYING:
                if self.controller:
                    self.controller.handle_event(event)
            
            elif self.state == GameState.END:
                if self.end_screen.handle_event(event):
                    self.start_new_game()
        
        return True
    
    def update(self):
        if self.state == GameState.LOADING:
            self.check_generation_complete()
        
        elif self.state == GameState.PLAYING:
            if self.controller:
                self.controller.update()
                tilt_x, tilt_y = self.controller.get_tilt()
                self.labyrinth_3d.set_tilt(tilt_x, tilt_y)
                
                gx, gy = self.labyrinth_3d.get_gravity()
                self.ball.apply_gravity(gx, gy)
            
            if self.ball and self.generator:
                walls = self.generator.get_walls()
                cell_size = self.generator.cell_size
                
                self.ball.apply_friction()
                self.ball.check_wall_collision(
                    walls, cell_size, 
                    self.generator.width, self.generator.height
                )
                self.ball.move()
                
                goal_pos = self.generator.get_end_position()
                if self.ball.check_goal(goal_pos[0], goal_pos[1]):
                    self.timer.stop()
                    self.end_screen.set_final_time(self.timer.format_time())
                    self.state = GameState.END
    
    def draw(self):
        if self.state == GameState.START:
            self.start_screen.draw(self.screen)
        
        elif self.state == GameState.LOADING:
            self.loading_screen.draw(self.screen)
        
        elif self.state == GameState.PLAYING:
            if self.labyrinth_3d and self.ball and self.controller:
                tilt_x, tilt_y = self.controller.get_tilt()
                self.game_screen.draw(self.screen, self.labyrinth_3d, self.ball, self.timer, tilt_x, tilt_y)
        
        elif self.state == GameState.END:
            if self.labyrinth_3d and self.ball:
                tilt_x, tilt_y = 0, 0
                self.game_screen.draw(self.screen, self.labyrinth_3d, self.ball, self.timer, tilt_x, tilt_y)
            self.end_screen.draw(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    game = Game(width=800, height=600)
    game.run()


if __name__ == "__main__":
    main()
