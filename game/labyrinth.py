import random
import threading
import math
from collections import deque


class LabyrinthGenerator:
    def __init__(self, width=15, height=15):
        self.width = width if width % 2 == 1 else width + 1
        self.height = height if height % 2 == 1 else height + 1
        self.grid = []
        self.start_pos = None
        self.end_pos = None
        self.cell_size = 50
        self.wall_height = 25
        self.generation_lock = threading.Lock()
        
    def generate(self):
        with self.generation_lock:
            self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
            
            def backtrack(x, y):
                self.grid[y][x] = 0
                directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
                random.shuffle(directions)
                
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 < nx < self.width - 1 and 0 < ny < self.height - 1 and self.grid[ny][nx] == 1:
                        self.grid[y + dy//2][x + dx//2] = 0
                        backtrack(nx, ny)
            
            backtrack(1, 1)
            
            self._find_start_end()
            return self.grid
    
    def _find_start_end(self):
        passages = [(x, y) for y in range(self.height) for x in range(self.width) 
                    if self.grid[y][x] == 0]
        
        max_dist = 0
        best_start = None
        best_end = None
        
        for _ in range(min(50, len(passages))):
            start = random.choice(passages)
            distances = self._bfs_distances(start)
            
            farthest = max(distances, key=distances.get, default=start)
            dist = distances.get(farthest, 0)
            
            if dist > max_dist:
                max_dist = dist
                best_start = start
                best_end = farthest
        
        self.start_pos = best_start if best_start else (1, 1)
        self.end_pos = best_end if best_end else (self.width - 2, self.height - 2)
        
        self.grid[self.start_pos[1]][self.start_pos[0]] = 0
        self.grid[self.end_pos[1]][self.end_pos[0]] = 0
    
    def _bfs_distances(self, start):
        distances = {}
        queue = deque([start])
        visited = set([start])
        
        while queue:
            x, y = queue.popleft()
            distances[(x, y)] = len(distances)
            
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and 
                    self.grid[ny][nx] == 0 and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        
        return distances
    
    def is_wall(self, x, y):
        grid_x = int(x // self.cell_size)
        grid_y = int(y // self.cell_size)
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.grid[grid_y][grid_x] == 1
        return True
    
    def get_walls(self):
        walls = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 1:
                    walls.append((x * self.cell_size, y * self.cell_size, 
                                  self.cell_size, self.cell_size))
        return walls
    
    def get_start_position(self):
        return (self.start_pos[0] * self.cell_size + self.cell_size // 2,
                self.start_pos[1] * self.cell_size + self.cell_size // 2)
    
    def get_end_position(self):
        return (self.end_pos[0] * self.cell_size + self.cell_size // 2,
                self.end_pos[1] * self.cell_size + self.cell_size // 2)
    
    def get_pixel_size(self):
        return (self.width * self.cell_size, self.height * self.cell_size)


class Labyrinth3D:
    def __init__(self, generator, screen_width=800, screen_height=600):
        self.generator = generator
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tilt_x = 0
        self.tilt_y = 0
        self.max_tilt = 20
        
        pixel_w, pixel_h = generator.get_pixel_size()
        self.base_offset_x = (screen_width - pixel_w) // 2
        self.base_offset_y = (screen_height - pixel_h) // 2 + 50
    
    def set_tilt(self, tilt_x, tilt_y):
        self.tilt_x = max(-self.max_tilt, min(self.max_tilt, tilt_x))
        self.tilt_y = max(-self.max_tilt, min(self.max_tilt, tilt_y))
    
    def get_gravity(self):
        gravity_strength = 0.3
        return (self.tilt_x * gravity_strength / self.max_tilt,
                self.tilt_y * gravity_strength / self.max_tilt)
    
    def world_to_screen(self, world_x, world_y, height_offset=0):
        tilt_offset_x = self.tilt_x * 2.5
        tilt_offset_y = self.tilt_y * 2.5
        
        screen_x = world_x + self.base_offset_x + tilt_offset_x
        screen_y = world_y + self.base_offset_y + tilt_offset_y - height_offset
        
        return (screen_x, screen_y)
    
    def get_draw_data(self):
        cell_size = self.generator.cell_size
        wall_height = self.generator.wall_height
        
        all_draw_items = []
        
        for gy in range(self.generator.height):
            for gx in range(self.generator.width):
                if self.generator.grid[gy][gx] == 0:
                    wx = gx * cell_size
                    wy = gy * cell_size
                    
                    floor_depth = wy + cell_size
                    all_draw_items.append({
                        'type': 'floor',
                        'depth': floor_depth,
                        'gx': gx,
                        'gy': gy,
                        'wx': wx,
                        'wy': wy,
                        'cell_size': cell_size
                    })
        
        for gy in range(self.generator.height):
            for gx in range(self.generator.width):
                if self.generator.grid[gy][gx] == 1:
                    wx = gx * cell_size
                    wy = gy * cell_size
                    
                    wall_depth = wy + cell_size
                    all_draw_items.append({
                        'type': 'wall',
                        'depth': wall_depth,
                        'gx': gx,
                        'gy': gy,
                        'wx': wx,
                        'wy': wy,
                        'cell_size': cell_size,
                        'wall_height': wall_height
                    })
        
        all_draw_items.sort(key=lambda x: x['depth'])
        
        return all_draw_items
    
    def render_floor(self, item):
        wx = item['wx']
        wy = item['wy']
        cell_size = item['cell_size']
        gx = item['gx']
        gy = item['gy']
        
        top_left = self.world_to_screen(wx, wy, 0)
        top_right = self.world_to_screen(wx + cell_size, wy, 0)
        bottom_right = self.world_to_screen(wx + cell_size, wy + cell_size, 0)
        bottom_left = self.world_to_screen(wx, wy + cell_size, 0)
        
        if (gx + gy) % 2 == 0:
            color = (210, 210, 200)
        else:
            color = (195, 195, 185)
        
        return {
            'polygon': [top_left, top_right, bottom_right, bottom_left],
            'color': color
        }
    
    def render_wall(self, item):
        wx = item['wx']
        wy = item['wy']
        cell_size = item['cell_size']
        wall_height = item['wall_height']
        
        faces = []
        
        top_left_base = self.world_to_screen(wx, wy, 0)
        top_right_base = self.world_to_screen(wx + cell_size, wy, 0)
        bottom_right_base = self.world_to_screen(wx + cell_size, wy + cell_size, 0)
        bottom_left_base = self.world_to_screen(wx, wy + cell_size, 0)
        
        top_left_top = self.world_to_screen(wx, wy, wall_height)
        top_right_top = self.world_to_screen(wx + cell_size, wy, wall_height)
        bottom_right_top = self.world_to_screen(wx + cell_size, wy + cell_size, wall_height)
        bottom_left_top = self.world_to_screen(wx, wy + cell_size, wall_height)
        
        if self.tilt_y >= 0:
            faces.append({
                'polygon': [bottom_left_base, bottom_right_base, bottom_right_top, bottom_left_top],
                'color': (80, 80, 80)
            })
        else:
            faces.append({
                'polygon': [top_left_base, top_right_base, top_right_top, top_left_top],
                'color': (90, 90, 90)
            })
        
        if self.tilt_x >= 0:
            faces.append({
                'polygon': [top_right_base, bottom_right_base, bottom_right_top, top_right_top],
                'color': (70, 70, 70)
            })
        else:
            faces.append({
                'polygon': [top_left_base, bottom_left_base, bottom_left_top, top_left_top],
                'color': (85, 85, 85)
            })
        
        faces.append({
            'polygon': [top_left_top, top_right_top, bottom_right_top, bottom_left_top],
            'color': (120, 120, 120)
        })
        
        return faces
    
    def get_ball_screen_pos(self, ball_x, ball_y):
        return self.world_to_screen(ball_x, ball_y, 0)
    
    def get_goal_screen_pos(self):
        goal_pos = self.generator.get_end_position()
        return self.world_to_screen(goal_pos[0], goal_pos[1], 0)
