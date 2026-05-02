import math


class Ball:
    def __init__(self, x, y, radius=12):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = 0
        self.vy = 0
        self.mass = 1.0
        self.friction = 0.98
        self.bounce_factor = 0.4
        self.min_velocity = 0.05
        self.max_speed = 8.0
        
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
    
    def apply_gravity(self, gx, gy):
        self.vx += gx / self.mass
        self.vy += gy / self.mass
        
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vx *= scale
            self.vy *= scale
    
    def apply_friction(self):
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if speed > 0:
            friction_factor = self.friction
            if speed < 1.0:
                friction_factor = self.friction * (0.9 + 0.1 * speed)
            self.vx *= friction_factor
            self.vy *= friction_factor
        
        if abs(self.vx) < self.min_velocity:
            self.vx = 0
        if abs(self.vy) < self.min_velocity:
            self.vy = 0
    
    def get_next_position(self):
        return (self.x + self.vx, self.y + self.vy)
    
    def move(self):
        self.x += self.vx
        self.y += self.vy
    
    def check_wall_collision(self, walls, cell_size, grid_width, grid_height):
        max_x = grid_width * cell_size
        max_y = grid_height * cell_size
        
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = abs(self.vx) * self.bounce_factor
        
        if self.x + self.radius > max_x:
            self.x = max_x - self.radius
            self.vx = -abs(self.vx) * self.bounce_factor
        
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = abs(self.vy) * self.bounce_factor
        
        if self.y + self.radius > max_y:
            self.y = max_y - self.radius
            self.vy = -abs(self.vy) * self.bounce_factor
        
        next_x, next_y = self.get_next_position()
        
        test_next_x = max(self.radius, min(max_x - self.radius, next_x))
        test_next_y = max(self.radius, min(max_y - self.radius, next_y))
        
        def get_grid_pos(pos):
            return int(pos // cell_size)
        
        def check_single_wall(wall_x, wall_y, test_x, test_y):
            wall_right = wall_x + cell_size
            wall_bottom = wall_y + cell_size
            
            closest_x = max(wall_x, min(test_x, wall_right))
            closest_y = max(wall_y, min(test_y, wall_bottom))
            
            dx = test_x - closest_x
            dy = test_y - closest_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < self.radius:
                return True, closest_x, closest_y, distance
            return False, closest_x, closest_y, distance
        
        current_grid_x = get_grid_pos(self.x)
        current_grid_y = get_grid_pos(self.y)
        next_grid_x = get_grid_pos(test_next_x)
        next_grid_y = get_grid_pos(test_next_y)
        
        grids_to_check = set()
        for gy in range(current_grid_y - 1, current_grid_y + 2):
            for gx in range(current_grid_x - 1, current_grid_x + 2):
                if 0 <= gx < grid_width and 0 <= gy < grid_height:
                    grids_to_check.add((gx, gy))
        for gy in range(next_grid_y - 1, next_grid_y + 2):
            for gx in range(next_grid_x - 1, next_grid_x + 2):
                if 0 <= gx < grid_width and 0 <= gy < grid_height:
                    grids_to_check.add((gx, gy))
        
        for gx, gy in grids_to_check:
            wall_x = gx * cell_size
            wall_y = gy * cell_size
            
            has_wall = False
            for wall in walls:
                if wall[0] == wall_x and wall[1] == wall_y:
                    has_wall = True
                    break
            
            if has_wall:
                collided, cx, cy, dist = check_single_wall(wall_x, wall_y, self.x, self.y)
                
                if collided:
                    if dist == 0:
                        dist = 0.1
                        dx = self.x - cx
                        dy = self.y - cy
                        if dx == 0 and dy == 0:
                            center_x = wall_x + cell_size / 2
                            center_y = wall_y + cell_size / 2
                            dx = self.x - center_x
                            dy = self.y - center_y
                            if dx == 0 and dy == 0:
                                dx = 1
                                dy = 1
                    else:
                        dx = self.x - cx
                        dy = self.y - cy
                    
                    nx = dx / dist
                    ny = dy / dist
                    
                    overlap = self.radius - dist
                    if overlap > 0:
                        self.x += nx * (overlap + 0.5)
                        self.y += ny * (overlap + 0.5)
                    
                    dot = self.vx * nx + self.vy * ny
                    if dot < 0:
                        self.vx -= (1 + self.bounce_factor) * dot * nx
                        self.vy -= (1 + self.bounce_factor) * dot * ny
        
        self.x = max(self.radius, min(max_x - self.radius, self.x))
        self.y = max(self.radius, min(max_y - self.radius, self.y))
        
        return False
    
    def check_goal(self, goal_x, goal_y, tolerance=18):
        dx = self.x - goal_x
        dy = self.y - goal_y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < tolerance
    
    def get_draw_position(self):
        return (int(self.x), int(self.y))
