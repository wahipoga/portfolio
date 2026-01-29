import raylibpy as rl
import random
import os
import math

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
GRAVITY = 0.6
JUMP_FORCE = -15
GAME_SPEED_INITIAL = 3
GAME_SPEED_INCREMENT = 0.0005
GROUND_HEIGHT = 50
CACTUS_MIN_HEIGHT = 40
CACTUS_MAX_HEIGHT = 60
BIRD_MIN_HEIGHT = 150
BIRD_MAX_HEIGHT = 250
CLOUD_SPEED = 1

# Colors
WHITE = rl.Color(255, 255, 255, 255)
RED = rl.Color(220, 60, 60, 255)
BLUE = rl.Color(80, 160, 255, 255)
GREEN = rl.Color(100, 220, 100, 255)
BLACK = rl.Color(30, 30, 30, 255)
GRAY = rl.Color(120, 120, 120, 255)
LIGHT_GRAY = rl.Color(220, 220, 220, 255)
DARK_GRAY = rl.Color(70, 70, 70, 255)
YELLOW = rl.Color(255, 215, 0, 255)
PURPLE = rl.Color(180, 80, 220, 255)
ORANGE = rl.Color(255, 140, 0, 255)
LIGHT_BLUE = rl.Color(180, 220, 240, 255)
SKY_BLUE = rl.Color(135, 206, 235, 255)
SUN_YELLOW = rl.Color(255, 230, 100, 255)
BUTTON_COLOR = rl.Color(80, 160, 255, 200)
BUTTON_HOVER = rl.Color(100, 180, 255, 230)
SHADOW_COLOR = rl.Color(0, 0, 0, 100)
NEON_PINK = rl.Color(255, 20, 147, 255)
NEON_GREEN = rl.Color(57, 255, 20, 255)
NEON_BLUE = rl.Color(0, 191, 255, 255)

# Game states
class GameState:
    MENU = 0
    PLAYING = 1
    CONTROLS = 2
    CREDITS = 3
    GAME_OVER = 4

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = rl.Rectangle(x, y, width, height)
        self.text = text
        self.color = BUTTON_COLOR
        self.hover_color = BUTTON_HOVER
        self.text_color = WHITE
        self.is_hovered = False
        self.font_size = 24
        self.shadow_offset = 3
        
    def update(self):
        mouse_pos = rl.get_mouse_position()
        self.is_hovered = rl.check_collision_point_rec(mouse_pos, self.rect)
        
    def draw(self):
        # Draw shadow
        shadow_rect = rl.Rectangle(self.rect.x + self.shadow_offset, 
                                  self.rect.y + self.shadow_offset, 
                                  self.rect.width, self.rect.height)
        rl.draw_rectangle_rounded(shadow_rect, 0.3, 6, SHADOW_COLOR)
        
        # Draw button
        color = self.hover_color if self.is_hovered else self.color
        rl.draw_rectangle_rounded(self.rect, 0.3, 6, color)
        rl.draw_rectangle_rounded_lines(self.rect, 0.3, 6, WHITE)
        
        # Draw text
        text_width = rl.measure_text(self.text, self.font_size)
        text_x = self.rect.x + (self.rect.width - text_width) // 2
        text_y = self.rect.y + (self.rect.height - self.font_size) // 2
        rl.draw_text(self.text, int(text_x), int(text_y), self.font_size, self.text_color)
        
    def is_clicked(self):
        return self.is_hovered and rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT)

class Dinosaur:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = 80
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.velocity_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.duck_height = 30
        self.normal_height = 60
        self.color = WHITE
        self.eye_color = BLACK
        self.mouth_color = BLACK
        
        # Buff system
        self.buffs = {
            "double_jump": {"active": False, "timer": 0, "max_time": 250, "jumps_remaining": 2},  # Less time
            "giant": {"active": False, "timer": 0, "max_time": 350},  # Less time
            "invincible": {"active": False, "timer": 0, "max_time": 400},  # Less time
            "weapon": {"active": False, "timer": 0, "max_time": 450, "bullets": []}  # Less time
        }
        
    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = JUMP_FORCE
            if self.buffs["double_jump"]["active"] and self.buffs["double_jump"]["jumps_remaining"] > 0:
                self.buffs["double_jump"]["jumps_remaining"] -= 1
        elif self.buffs["double_jump"]["active"] and self.buffs["double_jump"]["jumps_remaining"] > 0:
            self.velocity_y = JUMP_FORCE * 0.8
            self.buffs["double_jump"]["jumps_remaining"] -= 1
            self.is_jumping = True
            
    def duck(self, is_ducking):
        self.is_ducking = is_ducking
        if is_ducking:
            self.height = self.duck_height
        else:
            self.height = self.normal_height
            if not self.is_jumping:
                self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
            
    def update(self):
        # Jump movement
        if self.is_jumping:
            self.velocity_y += GRAVITY
            self.y += self.velocity_y
            
            if self.y >= SCREEN_HEIGHT - GROUND_HEIGHT - self.height:
                self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
                self.is_jumping = False
                self.velocity_y = 0
                if self.buffs["double_jump"]["active"]:
                    self.buffs["double_jump"]["jumps_remaining"] = 2
                    
        # Update buffs
        for buff_name in list(self.buffs.keys()):
            buff_data = self.buffs[buff_name]
            if buff_data["active"]:
                buff_data["timer"] += 1
                if buff_data["timer"] >= buff_data["max_time"]:
                    self.remove_buff(buff_name)
                    
        # Update projectiles
        if self.buffs["weapon"]["active"]:
            bullets_to_remove = []
            for i, bullet in enumerate(self.buffs["weapon"]["bullets"]):
                bullet["x"] += 15  # Faster
                if bullet["x"] > SCREEN_WIDTH + 50:
                    bullets_to_remove.append(i)
            
            for i in reversed(bullets_to_remove):
                self.buffs["weapon"]["bullets"].pop(i)
                    
    def activate_buff(self, buff_type):
        if buff_type in self.buffs:
            if buff_type == "double_jump":
                self.buffs[buff_type]["active"] = True
                self.buffs[buff_type]["timer"] = 0
                self.buffs[buff_type]["jumps_remaining"] = 2
            elif buff_type == "giant":
                self.buffs[buff_type]["active"] = True
                self.buffs[buff_type]["timer"] = 0
            elif buff_type == "invincible":
                self.buffs[buff_type]["active"] = True
                self.buffs[buff_type]["timer"] = 0
            elif buff_type == "weapon":
                self.buffs[buff_type]["active"] = True
                self.buffs[buff_type]["timer"] = 0
                self.buffs[buff_type]["bullets"] = []
                
    def remove_buff(self, buff_type):
        if buff_type in self.buffs:
            self.buffs[buff_type]["active"] = False
            self.buffs[buff_type]["timer"] = 0
            if "bullets" in self.buffs[buff_type]:
                self.buffs[buff_type]["bullets"] = []
            
    def shoot(self):
        if self.buffs["weapon"]["active"] and len(self.buffs["weapon"]["bullets"]) < 3:  # Less bullets
            bullet_y = self.y + self.height / 2 - 5
            self.buffs["weapon"]["bullets"].append({
                "x": self.x + self.width,
                "y": bullet_y,
                "width": 20,  # Wider
                "height": 8   # Lower
            })
            
    def get_rect(self):
        current_width = self.width
        current_height = self.height
        
        if self.buffs["giant"]["active"]:
            current_width = int(self.width * 1.5)
            current_height = int(self.height * 1.5)
            
        return rl.Rectangle(int(self.x), int(self.y), current_width, current_height)
        
    def draw(self):
        current_width = self.width
        current_height = self.height
        current_color = self.color
        
        # Apply buffs
        if self.buffs["giant"]["active"]:
            current_width = int(self.width * 1.5)
            current_height = int(self.height * 1.5)
            
        if self.buffs["invincible"]["active"]:
            if (self.buffs["invincible"]["timer"] // 8) % 2 == 0:  # Faster blinking
                current_color = YELLOW
                
        # Draw shadow
        shadow_offset = 3
        shadow_rect = rl.Rectangle(self.x + shadow_offset, self.y + shadow_offset, 
                                  current_width, current_height)
        rl.draw_rectangle_rounded(shadow_rect, 0.2, 4, SHADOW_COLOR)
        
        # Dinosaur body
        body_rect = rl.Rectangle(self.x, self.y, current_width, current_height)
        rl.draw_rectangle_rounded(body_rect, 0.2, 4, current_color)
        rl.draw_rectangle_rounded_lines(body_rect, 0.2, 4, BLACK)
        
        # Eyes
        eye_size = 6
        eye_x = self.x + current_width - 12
        eye_y = self.y + 12
        rl.draw_rectangle(int(eye_x), int(eye_y), eye_size, eye_size, self.eye_color)
        
        # Smile
        mouth_start_x = eye_x - 8
        mouth_end_x = eye_x + 4
        mouth_y = eye_y + 10
        rl.draw_line(int(mouth_start_x), int(mouth_y), int(mouth_end_x), int(mouth_y), self.mouth_color)
        
        # Draw projectiles
        if self.buffs["weapon"]["active"]:
            for bullet in self.buffs["weapon"]["bullets"]:
                # Shadow
                rl.draw_rectangle(int(bullet["x"] + 2), int(bullet["y"] + 2), 
                                 bullet["width"], bullet["height"], SHADOW_COLOR)
                # Bullet
                bullet_rect = rl.Rectangle(bullet["x"], bullet["y"], 
                                          bullet["width"], bullet["height"])
                rl.draw_rectangle_rounded(bullet_rect, 0.3, 3, PURPLE)
                rl.draw_rectangle_rounded_lines(bullet_rect, 0.3, 3, BLACK)
                
        # Draw buff indicators
        self.draw_buff_indicators()

    def draw_buff_indicators(self):
        indicator_y = 10
        indicator_size = 16
        spacing = 5
        
        active_buffs = [(name, data) for name, data in self.buffs.items() if data["active"]]
        
        for i, (buff_name, buff_data) in enumerate(active_buffs):
            indicator_x = 10 + i * (indicator_size + spacing)
            
            # Buff color
            if buff_name == "double_jump":
                buff_color = BLUE
            elif buff_name == "giant":
                buff_color = ORANGE
            elif buff_name == "invincible":
                buff_color = YELLOW
            elif buff_name == "weapon":
                buff_color = PURPLE
            else:
                buff_color = GREEN
                
            # Shadow
            rl.draw_rectangle(int(indicator_x + 1), int(indicator_y + 1), 
                             indicator_size, indicator_size, SHADOW_COLOR)
            
            # Indicator
            indicator_rect = rl.Rectangle(indicator_x, indicator_y, 
                                         indicator_size, indicator_size)
            rl.draw_rectangle_rounded(indicator_rect, 0.3, 4, buff_color)
            rl.draw_rectangle_rounded_lines(indicator_rect, 0.3, 4, BLACK)
            
            # Time bar
            time_ratio = 1 - (buff_data["timer"] / buff_data["max_time"])
            if time_ratio > 0:
                time_bar_height = int(indicator_size * time_ratio)
                time_bar_y = indicator_y + indicator_size - time_bar_height
                rl.draw_rectangle(int(indicator_x), int(time_bar_y), 
                                 indicator_size, time_bar_height, BLACK)

class Obstacle:
    def __init__(self, x, obstacle_type="cactus", difficulty_level=1, score=0):
        self.type = obstacle_type
        self.x = x
        self.passed = False
        self.destroyed = False
        
        # Size increases with difficulty AND score
        score_factor = min(score / 5000, 2.0)
        size_multiplier = 1.0 + (difficulty_level * 0.05) + (score_factor * 0.1)
        
        if self.type == "cactus":
            self.width = int(24 * size_multiplier)
            self.height = random.randint(int(CACTUS_MIN_HEIGHT * size_multiplier), 
                                        int(CACTUS_MAX_HEIGHT * size_multiplier))
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
            self.color = RED
            self.spikes_color = rl.Color(180, 40, 40, 255)
        else:  # bird - MORE DANGEROUS
            self.width = int(32 * size_multiplier)
            self.height = int(24 * size_multiplier)
            # Adjust bird height to be more challenging
            bird_y_min = BIRD_MIN_HEIGHT - (difficulty_level * 10)  # Lower
            bird_y_max = BIRD_MAX_HEIGHT - (difficulty_level * 20)  # Even lower
            bird_y_min = max(100, bird_y_min)  # Minimum 100
            bird_y_max = max(200, bird_y_max)  # Minimum 200
            
            # MORE BIRDS AT CHALLENGING HEIGHTS
            if random.random() < 0.7:  # 70% chance of medium/low height
                self.y = random.randint(int(bird_y_min), int((bird_y_min + bird_y_max) / 2))
            else:  # 30% chance of high height
                self.y = random.randint(int((bird_y_min + bird_y_max) / 2), int(bird_y_max))
                
            self.color = BLUE
            self.wing_up = True
            self.wing_timer = 0
            
    def update(self, game_speed):
        self.x -= game_speed * (1.1 if self.type == "bird" else 1.0)  # Birds faster
        
        if self.type == "bird":
            self.wing_timer += 1
            if self.wing_timer >= 8:  # Faster wings
                self.wing_up = not self.wing_up
                self.wing_timer = 0
                
    def draw(self):
        if not self.destroyed:
            # Shadow
            shadow_offset = 2
            shadow_y = self.y + shadow_offset if self.type == "cactus" else self.y + shadow_offset
            rl.draw_rectangle(int(self.x + shadow_offset), int(shadow_y), 
                             self.width, self.height, SHADOW_COLOR)
            
            # Main obstacle
            obstacle_rect = rl.Rectangle(self.x, self.y, self.width, self.height)
            rl.draw_rectangle_rounded(obstacle_rect, 0.2, 4, self.color)
            rl.draw_rectangle_rounded_lines(obstacle_rect, 0.2, 4, BLACK)
            
            # Details
            if self.type == "cactus":
                # Cactus spikes
                spike_width = 4
                spike_height = 8
                for i in range(3):
                    spike_x = self.x + (self.width // 2) - (spike_width // 2)
                    spike_y = self.y + 10 + (i * 15)
                    rl.draw_rectangle(int(spike_x), int(spike_y), spike_width, spike_height, self.spikes_color)
            else:
                # Bird wing
                wing_y = self.y - 4 if self.wing_up else self.y + 8  # Less wing movement
                wing_color = rl.Color(self.color.r - 30, self.color.g - 30, self.color.b - 30, 255)
                wing_rect = rl.Rectangle(self.x + 6, wing_y, 22, 12)
                rl.draw_rectangle_rounded(wing_rect, 0.3, 3, wing_color)
                rl.draw_rectangle_rounded_lines(wing_rect, 0.3, 3, BLACK)
                
    def get_rect(self):
        return rl.Rectangle(int(self.x), int(self.y), self.width, self.height)

class Buff:
    def __init__(self, x, difficulty_level=1, score=0):
        self.x = x
        self.width = 28
        self.height = 28
        
        # BUFFS IN MORE CHALLENGING POSITIONS
        # Higher difficulty and score make it harder to get
        score_factor = min(score / 10000, 1.0)
        
        # Base height - harder as progress
        if difficulty_level < 3:
            # Beginning: accessible buffs
            height_range = (100, SCREEN_HEIGHT - GROUND_HEIGHT - 100)
        elif difficulty_level < 6:
            # Medium: some difficult buffs
            if random.random() < 0.4:  # 40% difficult
                height_range = (50, 150)  # High
            else:
                height_range = (200, SCREEN_HEIGHT - GROUND_HEIGHT - 50)  # Low/medium
        else:
            # Difficult: majority difficult
            if random.random() < 0.7:  # 70% difficult
                height_range = (50, 180)  # High
            else:
                height_range = (250, SCREEN_HEIGHT - GROUND_HEIGHT - 80)  # Very low
                
        self.y = random.randint(int(height_range[0]), int(height_range[1]))
        self.color = GREEN
        self.collected = False
        
        # Buff types - LESS FREQUENT
        if difficulty_level < 3:
            self.types = ["double_jump", "invincible", "weapon", "giant"]
            weights = [0.3, 0.25, 0.25, 0.2]  # More balanced
        else:
            self.types = ["double_jump", "giant", "invincible", "weapon"]
            weights = [0.25, 0.25, 0.25, 0.25]  # Equally distributed
            
        self.type = random.choices(self.types, weights=weights)[0]
        
        # Colors
        if self.type == "double_jump":
            self.inner_color = BLUE
        elif self.type == "giant":
            self.inner_color = ORANGE
        elif self.type == "invincible":
            self.inner_color = YELLOW
        elif self.type == "weapon":
            self.inner_color = PURPLE
            
    def update(self, game_speed):
        self.x -= game_speed
        
    def draw(self):
        if not self.collected:
            # Shadow
            rl.draw_rectangle(int(self.x + 2), int(self.y + 2), 
                             self.width, self.height, SHADOW_COLOR)
            
            # Outer buff
            buff_rect = rl.Rectangle(self.x, self.y, self.width, self.height)
            rl.draw_rectangle_rounded(buff_rect, 0.3, 5, self.color)
            rl.draw_rectangle_rounded_lines(buff_rect, 0.3, 5, BLACK)
            
            # Inner buff
            inner_margin = 4
            inner_size = self.width - (inner_margin * 2)
            inner_rect = rl.Rectangle(self.x + inner_margin, self.y + inner_margin, 
                                      inner_size, inner_size)
            rl.draw_rectangle_rounded(inner_rect, 0.3, 4, self.inner_color)
            rl.draw_rectangle_rounded_lines(inner_rect, 0.3, 4, BLACK)
            
            # Symbol
            symbol_color = BLACK
            center_x = self.x + self.width / 2
            center_y = self.y + self.height / 2
            
            if self.type == "double_jump":
                rl.draw_text("2X", int(center_x - 9), int(center_y - 9), 11, symbol_color)
            elif self.type == "giant":
                rl.draw_text("G", int(center_x - 5), int(center_y - 9), 13, symbol_color)
            elif self.type == "invincible":
                rl.draw_text("S", int(center_x - 5), int(center_y - 9), 13, symbol_color)
            elif self.type == "weapon":
                rl.draw_text("W", int(center_x - 6), int(center_y - 9), 13, symbol_color)
                
    def get_rect(self):
        return rl.Rectangle(int(self.x), int(self.y), self.width, self.height)

class Game:
    def __init__(self):
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.game_speed = GAME_SPEED_INITIAL
        self.score = 0
        self.high_score = 0
        self.game_state = GameState.MENU
        self.difficulty_level = 1
        self.distance_traveled = 0
        self.game_time = 0
        
        self.dinosaur = Dinosaur()
        self.obstacles = []
        self.buffs = []
        self.clouds = []
        
        # Optimization - adjusted limits
        self.max_obstacles = 12
        self.max_buffs = 5  # LESS BUFFS
        self.max_clouds = 6
        
        self.obstacle_timer = 0
        self.obstacle_frequency = 100  # MORE OBSTACLES
        self.buff_timer = 0
        self.buff_frequency = 500  # BUFFS LESS FREQUENT
        self.cloud_timer = 0
        
        # Menu buttons
        button_width = 220
        button_height = 55
        button_x = (SCREEN_WIDTH - button_width) // 2
        
        self.play_button = Button(button_x, 220, button_width, button_height, "▶ PLAY")
        self.controls_button = Button(button_x, 290, button_width, button_height, "🎮 CONTROLS")
        self.credits_button = Button(button_x, 360, button_width, button_height, "📝 CREDITS")
        self.back_button = Button(20, 20, 100, 40, "🔙 BACK")
        
        # Load high score
        self.load_high_score()
        
    def load_high_score(self):
        try:
            if os.path.exists("super_square_run_highscore.txt"):
                with open("super_square_run_highscore.txt", "r") as f:
                    self.high_score = int(f.read())
        except:
            self.high_score = 0
            
    def save_high_score(self):
        try:
            with open("super_square_run_highscore.txt", "w") as f:
                f.write(str(int(self.high_score)))
        except:
            pass
        
    def reset(self):
        self.dinosaur = Dinosaur()
        self.obstacles.clear()
        self.buffs.clear()
        self.clouds.clear()
        self.game_speed = GAME_SPEED_INITIAL
        self.score = 0
        self.distance_traveled = 0
        self.game_time = 0
        self.difficulty_level = 1
        self.game_state = GameState.PLAYING
        self.obstacle_timer = 0
        self.buff_timer = 0
        self.obstacle_frequency = 100
        
    def update_difficulty(self):
        self.distance_traveled += self.game_speed
        self.game_time += 1
        
        # Increase difficulty faster
        score_factor = self.score / 800  # Faster
        time_factor = self.game_time / 4000  # Faster
        combined_factor = score_factor + time_factor
        
        # More aggressive level system
        new_level = 1 + int(combined_factor * 3)
        
        if new_level > self.difficulty_level:
            self.difficulty_level = new_level
            
        # Increase speed faster
        score_speed_boost = min(self.score / 3000, 4.0)  # Up to 4.0 boost
        self.game_speed = GAME_SPEED_INITIAL + (self.difficulty_level * 0.7) + score_speed_boost
        
        # Adjust obstacle frequency - MORE OBSTACLES
        base_frequency = 100
        min_frequency = 15  # Many more obstacles
        level_reduction = self.difficulty_level * 10
        score_reduction = min(int(self.score / 150), 50)
        
        self.obstacle_frequency = max(min_frequency, 
                                     base_frequency - level_reduction - score_reduction)
        
    def update(self):
        if self.game_state == GameState.MENU:
            self.play_button.update()
            self.controls_button.update()
            self.credits_button.update()
            
            if self.play_button.is_clicked():
                self.reset()
            elif self.controls_button.is_clicked():
                self.game_state = GameState.CONTROLS
            elif self.credits_button.is_clicked():
                self.game_state = GameState.CREDITS
                
        elif self.game_state in [GameState.CONTROLS, GameState.CREDITS]:
            self.back_button.update()
            if self.back_button.is_clicked():
                self.game_state = GameState.MENU
                
        elif self.game_state == GameState.PLAYING:
            self.dinosaur.update()
            self.update_difficulty()
            
            # Faster speed increase
            score_speed_increment = min(self.score / 30000, 0.003)
            self.game_speed += GAME_SPEED_INCREMENT + score_speed_increment
            
            # Update score
            self.score += 0.1 * (1 + self.difficulty_level * 0.15)
            
            # Remove off-screen objects
            self.cleanup_off_screen_objects()
            
            # Update obstacles
            for obstacle in self.obstacles:
                obstacle.update(self.game_speed)
                
                # Collision with dinosaur
                if not self.dinosaur.buffs["invincible"]["active"]:
                    if rl.check_collision_recs(self.dinosaur.get_rect(), obstacle.get_rect()):
                        self.game_state = GameState.GAME_OVER
                        if self.score > self.high_score:
                            self.high_score = self.score
                            self.save_high_score()
                
                # COLLISION WITH PROJECTILES - FIXED
                if self.dinosaur.buffs["weapon"]["active"]:
                    bullets_to_remove = []
                    for bullet in self.dinosaur.buffs["weapon"]["bullets"]:
                        bullet_rect = rl.Rectangle(bullet["x"], bullet["y"], 
                                                  bullet["width"], bullet["height"])
                        if rl.check_collision_recs(bullet_rect, obstacle.get_rect()):
                            obstacle.destroyed = True
                            self.score += 20  # More points for destroying
                            bullets_to_remove.append(bullet)
                    
                    # Remove bullets that hit
                    for bullet in bullets_to_remove:
                        if bullet in self.dinosaur.buffs["weapon"]["bullets"]:
                            self.dinosaur.buffs["weapon"]["bullets"].remove(bullet)
                
                # Mark as passed
                if not obstacle.passed and obstacle.x < self.dinosaur.x:
                    obstacle.passed = True
                    self.score += 5
            
            # Buffs
            for buff in self.buffs:
                buff.update(self.game_speed)
                
                if rl.check_collision_recs(self.dinosaur.get_rect(), buff.get_rect()):
                    buff.collected = True
                    self.dinosaur.activate_buff(buff.type)
                    self.score += 30  # More points for collecting hard buff
            
            # Clouds
            for cloud in self.clouds:
                cloud["x"] -= cloud["speed"]
            
            # Generate obstacles - MORE CHALLENGING
            self.obstacle_timer += 1
            if self.obstacle_timer >= self.obstacle_frequency and len(self.obstacles) < self.max_obstacles:
                self.obstacle_timer = 0
                
                # MORE BIRDS as difficulty increases
                cactus_chance = 0.7 - (self.difficulty_level * 0.04)  # Less cacti
                cactus_chance = max(0.4, cactus_chance)  # Minimum 40%
                
                obstacle_type = "cactus" if random.random() < cactus_chance else "bird"
                
                # Add obstacle
                self.obstacles.append(Obstacle(SCREEN_WIDTH, obstacle_type, self.difficulty_level, self.score))
                
                # MORE CHANCE FOR DOUBLE OBSTACLES
                if self.difficulty_level > 2 and random.random() < 0.4:
                    extra_type = "bird" if obstacle_type == "cactus" else "cactus"
                    extra_x = SCREEN_WIDTH + random.randint(30, 100)  # Closer
                    self.obstacles.append(Obstacle(extra_x, extra_type, self.difficulty_level, self.score))
            
            # Generate buffs - LESS FREQUENT AND HARDER
            self.buff_timer += 1
            buff_spawn_chance = 0.5 - (self.difficulty_level * 0.06)  # Less buffs
            buff_spawn_chance = max(0.2, buff_spawn_chance)  # Minimum 20%
            
            if (self.buff_timer >= self.buff_frequency and 
                len(self.buffs) < self.max_buffs and 
                random.random() < buff_spawn_chance):
                
                self.buff_timer = 0
                self.buffs.append(Buff(SCREEN_WIDTH, self.difficulty_level, self.score))
            
            # Generate clouds
            self.cloud_timer += 1
            if self.cloud_timer >= 100 and len(self.clouds) < self.max_clouds:
                self.cloud_timer = 0
                if random.random() < 0.4:
                    self.clouds.append(self.create_cloud())
                    
        elif self.game_state == GameState.GAME_OVER:
            if rl.is_key_pressed(rl.KEY_SPACE) or rl.is_key_pressed(rl.KEY_R) or rl.is_key_pressed(rl.KEY_ENTER):
                self.reset()
    
    def cleanup_off_screen_objects(self):
        """Remove objects completely off screen"""
        # Obstacles
        self.obstacles = [obs for obs in self.obstacles 
                         if obs.x > -100 and not obs.destroyed]
        
        # Buffs
        self.buffs = [buff for buff in self.buffs 
                     if buff.x > -100 and not buff.collected]
        
        # Clouds
        self.clouds = [cloud for cloud in self.clouds 
                      if cloud["x"] > -200]
                
    def create_cloud(self):
        return {
            "x": SCREEN_WIDTH + random.randint(0, 100),
            "y": random.randint(30, 150),
            "width": random.randint(60, 100),
            "height": random.randint(20, 40),
            "speed": CLOUD_SPEED + random.uniform(-0.3, 0.3),
            "color": LIGHT_GRAY
        }
        
    def draw_cloud(self, cloud):
        x, y, width, height = cloud["x"], cloud["y"], cloud["width"], cloud["height"]
        
        # Shadow
        shadow_rect = rl.Rectangle(x + 3, y + 3, width, height)
        rl.draw_rectangle_rounded(shadow_rect, 0.5, 8, SHADOW_COLOR)
        
        # Cloud
        cloud_rect = rl.Rectangle(x, y, width, height)
        rl.draw_rectangle_rounded(cloud_rect, 0.5, 8, cloud["color"])
        rl.draw_rectangle_rounded_lines(cloud_rect, 0.5, 8, WHITE)
        
    def draw_gradient_background(self):
        # Sky with gradient
        score_factor = min(self.score / 3000, 1.0)  # Faster
        
        top_color = rl.Color(
            int(10 + score_factor * 25),
            int(10 + score_factor * 12), 
            int(40 + score_factor * 25), 
            255
        )
        bottom_color = rl.Color(
            int(30 + score_factor * 35),
            int(30 + score_factor * 18), 
            int(80 + score_factor * 35), 
            255
        )
        
        rl.draw_rectangle_gradient_v(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, top_color, bottom_color)
        
        # Stars
        for i in range(50):
            star_x = (i * 37) % SCREEN_WIDTH
            star_y = (i * 23) % (SCREEN_HEIGHT - GROUND_HEIGHT)
            star_size = 1 + (i % 3)
            brightness = 150 + ((i + int(self.score/80)) % 105)
            rl.draw_rectangle(int(star_x), int(star_y), star_size, star_size, 
                             rl.Color(brightness, brightness, brightness, 255))
        
        # Ground
        ground_y = SCREEN_HEIGHT - GROUND_HEIGHT
        ground_darkness = min(40 + int(self.score/80), 100)
        rl.draw_rectangle_gradient_v(0, ground_y, SCREEN_WIDTH, GROUND_HEIGHT, 
                                    rl.Color(ground_darkness, ground_darkness, ground_darkness, 255), 
                                    rl.Color(20, 20, 20, 255))
        
        # Ground lines
        line_color = NEON_GREEN
        for i in range(0, SCREEN_WIDTH, 40):
            line_x = (i - int(self.score * 2) % 40) % SCREEN_WIDTH
            rl.draw_line(int(line_x), ground_y + 1, int(line_x + 20), ground_y + 1, 
                         rl.Color(line_color.r, line_color.g, line_color.b, 100))
            rl.draw_line(int(line_x), ground_y, int(line_x + 20), ground_y, line_color)
            
    def draw_menu(self):
        # SUPER SQUARE RUN title
        title = "SUPER SQUARE RUN"
        title_size = 52
        
        time = rl.get_time()
        glow_intensity = abs(math.sin(time * 2)) * 100 + 155
        
        for offset in range(3, 0, -1):
            glow_color = rl.Color(NEON_PINK.r, NEON_PINK.g, NEON_PINK.b, int(glow_intensity / offset))
            title_width = rl.measure_text(title, title_size + offset)
            rl.draw_text(title, (SCREEN_WIDTH - title_width) // 2 + offset, 
                        103 + offset, title_size + offset, glow_color)
        
        title_width = rl.measure_text(title, title_size)
        title_x = (SCREEN_WIDTH - title_width) // 2
        title_y = 100
        
        # Gradient in title
        for i, letter in enumerate(title):
            if letter != ' ':
                letter_x = title_x + rl.measure_text(title[:i], title_size)
                color_index = (i + int(time * 5)) % 3
                if color_index == 0:
                    letter_color = NEON_PINK
                elif color_index == 1:
                    letter_color = NEON_BLUE
                else:
                    letter_color = NEON_GREEN
                
                rl.draw_text(letter, int(letter_x), int(title_y), title_size, letter_color)
        
        # Subtitle with basic controls
        subtitle = "Press SPACE to jump • DOWN ARROW to duck"
        subtitle_width = rl.measure_text(subtitle, 22)
        rl.draw_text(subtitle, (SCREEN_WIDTH - subtitle_width) // 2, 170, 22, WHITE)
        
        # Draw floating game elements
        self.draw_floating_game_elements()
        
        # High score
        hs_text = f"🏆 HIGH SCORE: {int(self.high_score)}"
        hs_width = rl.measure_text(hs_text, 26)
        rl.draw_text(hs_text, (SCREEN_WIDTH - hs_width) // 2, 430, 26, YELLOW)
        
        # Buttons with icons
        self.play_button.draw()
        self.controls_button.draw()
        self.credits_button.draw()
        
        # Basic controls in menu
        controls_text = "ESC: Back to Menu • F: Shoot (with weapon)"
        controls_width = rl.measure_text(controls_text, 18)
        rl.draw_text(controls_text, (SCREEN_WIDTH - controls_width) // 2, 480, 18, LIGHT_GRAY)
        
    def draw_floating_game_elements(self):
        time = rl.get_time()
        
        # Floating dinosaur
        dino_size = 50
        dino_x = SCREEN_WIDTH * 0.2
        dino_y = 320 + math.sin(time * 2) * 10
        dino_rect = rl.Rectangle(dino_x - dino_size//2, dino_y - dino_size//2, 
                                dino_size, dino_size)
        rl.draw_rectangle_rounded(dino_rect, 0.2, 4, WHITE)
        rl.draw_rectangle_rounded_lines(dino_rect, 0.2, 4, BLACK)
        
        # Floating cactus
        cactus_x = SCREEN_WIDTH * 0.8
        cactus_y = 340 + math.sin(time * 2 + 1) * 8
        cactus_rect = rl.Rectangle(cactus_x - 12, cactus_y - 25, 24, 50)
        rl.draw_rectangle_rounded(cactus_rect, 0.2, 4, RED)
        rl.draw_rectangle_rounded_lines(cactus_rect, 0.2, 4, BLACK)
        
        # Floating buff
        buff_x = SCREEN_WIDTH * 0.5
        buff_y = 300 + math.sin(time * 2 + 2) * 12
        buff_rect = rl.Rectangle(buff_x - 14, buff_y - 14, 28, 28)
        rl.draw_rectangle_rounded(buff_rect, 0.3, 5, GREEN)
        rl.draw_rectangle_rounded_lines(buff_rect, 0.3, 5, BLACK)
        
        # Floating bird
        bird_x = SCREEN_WIDTH * 0.35
        bird_y = 280 + math.sin(time * 2 + 3) * 15
        bird_rect = rl.Rectangle(bird_x - 16, bird_y - 12, 32, 24)
        rl.draw_rectangle_rounded(bird_rect, 0.2, 4, BLUE)
        rl.draw_rectangle_rounded_lines(bird_rect, 0.2, 4, BLACK)
        
    def draw_controls(self):
        # Title
        title = "🎮 COMPLETE CONTROLS"
        title_width = rl.measure_text(title, 40)
        rl.draw_text(title, (SCREEN_WIDTH - title_width) // 2, 60, 40, NEON_BLUE)
        
        # Background for readability
        bg_rect = rl.Rectangle(40, 120, SCREEN_WIDTH - 80, 320)
        rl.draw_rectangle_rounded(bg_rect, 0.1, 6, rl.Color(0, 0, 0, 200))
        
        # Main controls section
        rl.draw_text("MAIN CONTROLS:", 60, 140, 26, NEON_GREEN)
        
        controls_main = [
            "SPACE or UP ARROW     →  JUMP",
            "DOWN ARROW            →  DUCK (avoids birds)",
            "F                     →  SHOOT (when you have weapon)",
            "ESC                   →  BACK TO MENU",
            "R or ENTER            →  RESTART (game over)"
        ]
        
        for i, line in enumerate(controls_main):
            rl.draw_text(line, 80, 180 + i * 30, 20, WHITE)
        
        # Buffs section
        rl.draw_text("⚡ SPECIAL BUFFS:", 60, 280, 26, YELLOW)
        
        buffs_info = [
            "Green squares give temporary powers:",
            "🔵 2X  →  DOUBLE JUMP (2 jumps in air)",
            "🟠 G   →  GIANT (bigger, runs over some obstacles)",
            "🟡 S   →  INVINCIBILITY (immune to damage, blinks)",
            "🟣 W   →  WEAPON (shoot with F, destroys obstacles)"
        ]
        
        for i, line in enumerate(buffs_info):
            rl.draw_text(line, 80, 320 + i * 25, 18, LIGHT_GRAY)
        
        # Tips
        tips_y = 420
        rl.draw_text("💡 TIPS:", 60, tips_y, 24, NEON_PINK)
        rl.draw_text("• Ducking is essential for passing low birds", 80, tips_y + 30, 18, LIGHT_GRAY)
        rl.draw_text("• Buffs become rarer and harder as you progress", 80, tips_y + 55, 18, LIGHT_GRAY)
        
        self.back_button.draw()
        
    def draw_credits(self):
        # Title
        title = "📝 CREDITS"
        title_width = rl.measure_text(title, 48)
        rl.draw_text(title, (SCREEN_WIDTH - title_width) // 2, 60, 48, NEON_PINK)
        
        # Background for readability
        bg_rect = rl.Rectangle(50, 120, SCREEN_WIDTH - 100, 300)
        rl.draw_rectangle_rounded(bg_rect, 0.1, 6, rl.Color(0, 0, 0, 180))
        
        # Credits
        credits = [
            "🎮 SUPER SQUARE RUN 🎮",
            "Balanced and Improved Version",
            "",
            "👨‍💻 DEVELOPER:",
            "wahipogo (wahi)",
            "",
            "🛠️ CURRENT VERSION:",
            "• Weapon WORKS and destroys obstacles",
            "• Buffs rarer and in challenging positions",
            "• Ducking is now USEFUL against low birds",
            "• Difficulty increases FASTER",
            "• Controls CLEARER and more intuitive",
            "",
            "✨ GOAL:",
            "Survive as long as possible in a",
            "progressively more challenging and dynamic game!"
        ]
        
        for i, line in enumerate(credits):
            line_width = rl.measure_text(line, 18)
            color = NEON_PINK if "🎮" in line else (WHITE if "👨" in line else 
                   (NEON_BLUE if "🛠️" in line else (NEON_GREEN if "🎨" in line else 
                   (YELLOW if "✨" in line else LIGHT_GRAY))))
            rl.draw_text(line, (SCREEN_WIDTH - line_width) // 2, 130 + i * 22, 18, color)
        
        self.back_button.draw()
        
    def draw_game(self):
        # Clouds
        for cloud in self.clouds:
            self.draw_cloud(cloud)
            
        # Buffs
        for buff in self.buffs:
            buff.draw()
            
        # Obstacles
        for obstacle in self.obstacles:
            obstacle.draw()
            
        # Dinosaur
        self.dinosaur.draw()
        
        # Game interface
        score_text = f"🏆 SCORE: {int(self.score)}"
        score_x = SCREEN_WIDTH - rl.measure_text(score_text, 26) - 20
        
        score_glow = min(100 + int(self.score / 80), 200)
        rl.draw_text(score_text, int(score_x + 2), 22, 26, rl.Color(255, 255, 255, score_glow))
        rl.draw_text(score_text, int(score_x), 20, 26, YELLOW)
        
        high_score_text = f"👑 HIGH SCORE: {int(self.high_score)}"
        high_score_x = SCREEN_WIDTH - rl.measure_text(high_score_text, 22) - 20
        rl.draw_text(high_score_text, int(high_score_x), 55, 22, NEON_GREEN)
        
        if self.game_state == GameState.PLAYING:
            # Left side information
            level_text = f"📊 LEVEL: {self.difficulty_level}"
            rl.draw_text(level_text, 20, 20, 22, WHITE)
            
            speed_text = f"⚡ SPEED: {self.game_speed:.1f}"
            rl.draw_text(speed_text, 20, 50, 18, LIGHT_GRAY)
            
            # Active controls on screen
            controls_y = 85
            rl.draw_text("🎮 CONTROLS:", 20, controls_y, 16, NEON_BLUE)
            rl.draw_text("SPACE: Jump  ↓: Duck  F: Shoot", 20, controls_y + 20, 14, LIGHT_GRAY)
            
            # Difficulty indicator
            diff_level = min(10, self.difficulty_level)
            diff_text = f"🔥 DIFFICULTY: {diff_level}/10"
            diff_width = rl.measure_text(diff_text, 18)
            diff_color = GREEN if diff_level < 4 else (YELLOW if diff_level < 7 else RED)
            rl.draw_text(diff_text, SCREEN_WIDTH - diff_width - 20, 85, 18, diff_color)
            
            # Visual difficulty bar
            bar_width = 200
            bar_height = 10
            bar_x = SCREEN_WIDTH - bar_width - 20
            bar_y = 110
            
            # Bar background
            rl.draw_rectangle(int(bar_x), int(bar_y), bar_width, bar_height, DARK_GRAY)
            
            # Fill bar
            fill_width = int(bar_width * (diff_level / 10))
            rl.draw_rectangle(int(bar_x), int(bar_y), fill_width, bar_height, diff_color)
            rl.draw_rectangle_lines(int(bar_x), int(bar_y), bar_width, bar_height, WHITE)
            
    def draw_game_over(self):
        # Dark overlay
        rl.draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, rl.Color(0, 0, 0, 180))
        
        # GAME OVER title
        game_over_text = "GAME OVER!"
        go_width = rl.measure_text(game_over_text, 60)
        
        time = rl.get_time()
        glow = abs(math.sin(time * 3)) * 100 + 155
        for offset in range(3, 0, -1):
            glow_color = rl.Color(255, 50, 50, int(glow / offset))
            rl.draw_text(game_over_text, (SCREEN_WIDTH - go_width) // 2 + offset, 
                        103 + offset, 60 + offset, glow_color)
        
        rl.draw_text(game_over_text, (SCREEN_WIDTH - go_width) // 2, 100, 60, RED)
        
        # Statistics
        score_text = f"🏆 Final Score: {int(self.score)}"
        level_text = f"📈 Level reached: {self.difficulty_level}"
        speed_text = f"⚡ Maximum speed: {self.game_speed:.1f}"
        restart_text = "🔄 Press SPACE, ENTER or R to play again"
        menu_text = "🏠 Press ESC to return to menu"
        
        score_width = rl.measure_text(score_text, 36)
        level_width = rl.measure_text(level_text, 28)
        speed_width = rl.measure_text(speed_text, 24)
        restart_width = rl.measure_text(restart_text, 20)
        menu_width = rl.measure_text(menu_text, 18)
        
        rl.draw_text(score_text, (SCREEN_WIDTH - score_width) // 2, 180, 36, YELLOW)
        rl.draw_text(level_text, (SCREEN_WIDTH - level_width) // 2, 230, 28, WHITE)
        rl.draw_text(speed_text, (SCREEN_WIDTH - speed_width) // 2, 270, 24, NEON_BLUE)
        rl.draw_text(restart_text, (SCREEN_WIDTH - restart_width) // 2, 320, 20, NEON_GREEN)
        rl.draw_text(menu_text, (SCREEN_WIDTH - menu_width) // 2, 350, 18, LIGHT_GRAY)
        
    def draw(self):
        self.draw_gradient_background()
        
        if self.game_state == GameState.MENU:
            self.draw_menu()
        elif self.game_state == GameState.CONTROLS:
            self.draw_controls()
        elif self.game_state == GameState.CREDITS:
            self.draw_credits()
        elif self.game_state == GameState.PLAYING:
            self.draw_game()
        elif self.game_state == GameState.GAME_OVER:
            self.draw_game()
            self.draw_game_over()

def main():
    # Initialize window
    rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "🎮 SUPER SQUARE RUN - wahipogo")
    
    # Performance settings
    rl.set_target_fps(60)
    
    game = Game()
    
    # Main game loop
    while not rl.window_should_close():
        # ESC key to return to menu
        if rl.is_key_pressed(rl.KEY_ESCAPE):
            if game.game_state in [GameState.PLAYING, GameState.GAME_OVER]:
                game.game_state = GameState.MENU
            elif game.game_state in [GameState.CONTROLS, GameState.CREDITS]:
                game.game_state = GameState.MENU
        
        # Game controls
        if game.game_state == GameState.PLAYING:
            if rl.is_key_pressed(rl.KEY_SPACE) or rl.is_key_pressed(rl.KEY_UP):
                game.dinosaur.jump()
                
            if rl.is_key_pressed(rl.KEY_F):
                game.dinosaur.shoot()
                
            # Duck - NOW USEFUL!
            if rl.is_key_down(rl.KEY_DOWN):
                game.dinosaur.duck(True)
            else:
                game.dinosaur.duck(False)
        
        # Update game logic
        game.update()
        
        # Draw
        rl.begin_drawing()
        game.draw()
        rl.end_drawing()
        
    # Close window
    rl.close_window()

if __name__ == "__main__":
    main()
