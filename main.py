import asyncio
import pygame
import math
import random
import os

# Ініціалізація
pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1300, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Бойові їжачки: Тактичний Рубіж")
clock = pygame.time.Clock()

FONT = pygame.font.Font(None, 24)
FONT_LARGE = pygame.font.Font(None, 38)
FONT_TITLE = pygame.font.Font(None, 68)

# Кольори UI та палітра
BG_COLOR = (142, 168, 77)
PATH_COLOR = (144, 104, 76)
PATH_BORDER = (92, 64, 46)
PATH_INNER_LINE = (122, 88, 62)
UI_BG = (18, 22, 30)
TEXT_COLOR = (240, 244, 250)
GOLD_COLOR = (255, 215, 60)
HEALTH_COLOR = (255, 75, 75)
ABILITY_COLOR = (0, 255, 180)
BORDER_COLOR = (58, 69, 92)

# Кольори для UI елементів та снарядів
COLOR_RIFLEMAN = (46, 204, 113)
COLOR_GRENADIER = (230, 126, 34)
COLOR_GATLING = (52, 152, 219)
COLOR_CANNON = (155, 89, 182)

# РОЗМІРИ ДЛЯ ЇЖАЧКІВ
TOWER_BASE_SIZE = (115, 135)
MAX_TOWERS = 6

BASE_TOWER_COSTS = {
    "rifleman": 50,
    "grenadier": 100,
    "gatling": 200,
    "cannon": 500
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_base_hp_color(hp):
    hp = max(0, min(100, hp))
    if hp >= 90:
        return (40, 220, 100)
    elif hp >= 50:
        factor = (hp - 50) / 40.0
        r = int(255 + (40 - 255) * factor)
        g = int(220 + (220 - 220) * factor)
        b = int(50 + (100 - 50) * factor)
        return (r, g, b)
    else:
        factor = hp / 50.0
        r = int(255 + (255 - 255) * factor)
        g = int(50 + (220 - 50) * factor)
        b = int(50 + (50 - 50) * factor)
        return (r, g, b)

def load_game_image(filename, target_size):
    try:
        full_path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(full_path):
            full_path = filename

        img = pygame.image.load(full_path).convert_alpha()
        img = pygame.transform.scale(img, target_size)
        img_flipped = pygame.transform.flip(img, True, False)
        return {"normal": img, "flipped": img_flipped}
    except pygame.error:
        surf = pygame.Surface(target_size, pygame.SRCALPHA)
        return {"normal": surf, "flipped": surf}

# Завантаження юнітів
IMG_RIFLEMAN = load_game_image("avtomatnyk.png", TOWER_BASE_SIZE)
IMG_GRENADIER = load_game_image("granatometnyk.png", TOWER_BASE_SIZE)
IMG_GATLING = load_game_image("kylemetnyk.png", TOWER_BASE_SIZE)
IMG_CANNON = load_game_image("pyshkar.png", TOWER_BASE_SIZE)

TOWER_IMAGES = {
    "rifleman": IMG_RIFLEMAN,
    "grenadier": IMG_GRENADIER,
    "gatling": IMG_GATLING,
    "cannon": IMG_CANNON
}

ENEMY_IMAGES = {
    "boss": load_game_image("boss.png", (145, 145)),
    "tank": load_game_image("mylyci.png", (115, 115)),
    "normal": load_game_image("jivchik.png", (95, 95)),
    "fast": load_game_image("velik.png", (85, 85)),
    "scout": load_game_image("mocik.png", (80, 80)),
    "bigyn": load_game_image("bigyn.png", (90, 90))
}

# ==========================================
# ЗАВАНТАЖЕННЯ АСЕТІВ ДЛЯ ОТОЧЕННЯ (PROPS)
# ==========================================
def load_prop_image(filename, target_size):
    try:
        full_path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(full_path):
            full_path = filename
        img = pygame.image.load(full_path).convert_alpha()
        return pygame.transform.scale(img, target_size)
    except pygame.error:
        surf = pygame.Surface(target_size, pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (40, 110, 50), (0, 0, target_size[0], target_size[1]))
        return surf

SPRITE_TREE_RAW = load_prop_image("tree_spruce.png", (95, 150))
SPRITE_BUSH = load_prop_image("prop_bush.png", (56, 48))
SPRITE_STONE = load_prop_image("prop_stone.png", (42, 35))
SPRITE_FLOWERS = load_prop_image("prop_flowers.png", (38, 38))

def generate_grass_background(tileset_filename, width, height, tile_size=80):
    full_path = os.path.join(BASE_DIR, tileset_filename)
    try:
        tileset_img = pygame.image.load(full_path).convert()
        grass_tile = tileset_img.subsurface(pygame.Rect(0, 0, tile_size, tile_size))
    except Exception:
        grass_tile = pygame.Surface((tile_size, tile_size))
        grass_tile.fill(BG_COLOR)

    bg_surface = pygame.Surface((width, height))
    for x in range(0, width, tile_size):
        for y in range(0, height, tile_size):
            bg_surface.blit(grass_tile, (x, y))
    return bg_surface

LEVELS = {
    1: [(0, 90), (450, 90), (450, 300), (250, 300), (250, 500), (700, 500), (700, 140), (1050, 140), (1050, 440), (1350, 440)],
    2: [(0, 300), (350, 300), (350, 100), (950, 100), (950, 500), (600, 500), (600, 290), (1150, 290), (1150, 460), (1350, 460)],
    3: [(0, 420), (400, 420), (400, 120), (800, 120), (800, 390), (1100, 390), (1100, 110), (1350, 110)],
    4: [(0, 170), (200, 170), (200, 420), (500, 420), (500, 100), (850, 100), (850, 470), (1100, 470), (1100, 220), (1350, 220)],
    5: [(0, 100), (900, 100), (900, 300), (150, 300), (150, 500), (1100, 500), (1100, 300), (1400, 300)]
}

current_level = 1
PATH = LEVELS[current_level]

def distance_to_segment(p, v, w):
    px, py = p
    vx, vy = v
    wx, wy = w
    l2 = (vx - wx)**2 + (vy - wy)**2
    if l2 == 0:
        return math.hypot(px - vx, py - vy)
    t = max(0, min(1, ((px - vx) * (wx - vx) + (py - vy) * (wy - vy)) / l2))
    projection_x = vx + t * (wx - vx)
    projection_y = vy + t * (wy - vy)
    return math.hypot(px - projection_x, py - projection_y)

def is_on_path(x, y, path_points, min_distance=85):
    for i in range(len(path_points) - 1):
        if distance_to_segment((x, y), path_points[i], path_points[i+1]) < min_distance:
            return True
    return False

# ==========================================
# ДЕКОРАЦІЇ ТА ПРИРОДНЕ ПОХИТУВАННЯ
# ==========================================
class EnvironmentObject:
    def __init__(self, x, y, obj_type):
        self.x = x
        self.y = y
        self.type = obj_type
        self.wind_offset = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(1.2, 1.5)

        if self.type == "tree":
            self.image = SPRITE_TREE_RAW
            self.shadow_size = (62, 20)
        elif self.type == "bush":
            self.image = SPRITE_BUSH
            self.shadow_size = (48, 16)
        elif self.type == "stone":
            self.image = SPRITE_STONE
            self.shadow_size = (38, 14)
        else:  # flowers
            self.image = SPRITE_FLOWERS
            self.shadow_size = (30, 12)

    def draw(self, surface, time_sec):
        sw, sh = self.shadow_size
        shadow_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, sw, sh))
        surface.blit(shadow_surf, (self.x - sw // 2, self.y - sh // 2))

        if self.type == "tree":
            sway = math.sin(time_sec * self.sway_speed + self.wind_offset) * 2.8
            w, h = self.image.get_size()
            
            step = 5
            for y_slice in range(0, h, step):
                slice_h = min(step, h - y_slice)
                height_ratio = (h - y_slice) / float(h)
                offset_x = sway * (height_ratio ** 1.6)
                
                slice_rect = pygame.Rect(0, y_slice, w, slice_h)
                surface.blit(self.image, (self.x - w // 2 + offset_x, self.y - h + y_slice), slice_rect)
        else:
            rect = self.image.get_rect(midbottom=(self.x, self.y))
            surface.blit(self.image, rect.topleft)

# Розташування для 1-ї карти за шаблоном
MAP_1_LAYOUT = [
    (145, 235, "tree"),
    (30, 580, "tree"),
    (540, 85, "tree"),
    (815, 420, "tree"),
    (835, 585, "tree"),
    (1150, 75, "tree"),
    (1240, 245, "tree"),

    (210, 35, "bush"),
    (65, 380, "bush"),
    (315, 185, "bush"),
    (430, 395, "bush"),
    (700, 50, "bush"),
    (755, 235, "bush"),
    (765, 570, "bush"),
    (1190, 85, "bush"),
    (1250, 335, "bush"),
    (1255, 545, "bush"),

    (20, 260, "flowers"),
    (130, 330, "flowers"),
    (95, 510, "flowers"),
    (545, 350, "flowers"),
    (760, 50, "flowers"),
    (765, 330, "flowers"),
    (735, 455, "flowers"),
    (925, 535, "flowers"),
    (1075, 50, "flowers"),

    (65, 195, "stone"),
    (145, 575, "stone"),
    (525, 220, "stone"),
    (865, 335, "stone"),
    (1130, 330, "stone"),
    (1255, 100, "stone")
]

def spawn_environment(path_points, level_num=1):
    objects = []
    if level_num == 1:
        for x, y, o_type in MAP_1_LAYOUT:
            min_d = 100 if o_type == "tree" else 75
            if not is_on_path(x, y, path_points, min_distance=min_d):
                objects.append(EnvironmentObject(x, y, o_type))
    else:
        prop_types = ["tree", "bush", "stone", "flowers", "bush"]
        attempts = 0
        while len(objects) < 26 and attempts < 4000:
            attempts += 1
            px = random.randint(50, WIDTH - 50)
            py = random.randint(70, 560)
            cur_type = random.choice(prop_types)
            min_dist = 120 if cur_type == "tree" else 85

            if not is_on_path(px, py, path_points, min_distance=min_dist):
                if all(math.hypot(px - o.x, py - o.y) >= 105 for o in objects):
                    objects.append(EnvironmentObject(px, py, cur_type))

    objects.sort(key=lambda o: o.y)
    return objects

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-2.5, 2.5)
        self.vy = random.uniform(-2.5, 2.5)
        self.radius = random.randint(2, 5)
        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 8
        if self.radius > 0.1:
            self.radius -= 0.05
        return self.alpha <= 0

    def draw(self, surface):
        if self.alpha > 0 and self.radius > 0:
            p_surface = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            r, g, b = self.color
            pygame.draw.circle(p_surface, (r, g, b, int(self.alpha)), (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(p_surface, (int(self.x - self.radius), int(self.y - self.radius)))

class FlashEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.max_radius = 65
        self.speed = 12
        self.alpha = 255

    def update(self):
        self.radius += self.speed
        self.alpha = max(0, int(255 * (1 - self.radius / self.max_radius)))
        return self.radius >= self.max_radius

    def draw(self, surface):
        if self.alpha > 0:
            flash_surf = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 255, 255, self.alpha), (self.max_radius, self.max_radius), int(self.radius))
            pygame.draw.circle(flash_surf, (220, 160, 255, int(self.alpha * 0.8)), (self.max_radius, self.max_radius), int(self.radius * 0.75))
            pygame.draw.circle(flash_surf, (255, 230, 255, self.alpha), (self.max_radius, self.max_radius), int(self.radius * 0.4))
            surface.blit(flash_surf, (int(self.x - self.max_radius), int(self.y - self.max_radius)))

class Enemy:
    def __init__(self, wave, enemy_type, speed_modifier, reward_modifier, is_fast_boss=False):
        self.target_idx = 1
        self.slow_timer = 0 
        self.type = enemy_type
        self.facing_right = True  
        self.pending_reward_fraction = 0.0
        self.is_fast_boss = is_fast_boss
        
        # Широкий коридор маневру вздовж ширини дороги (+-34 пікселі)
        self.lane_offset = random.uniform(-34, 34)
        self.wander_phase = random.uniform(0, math.pi * 2)
        self.wander_speed = random.uniform(0.04, 0.08)
        
        # Початкове позиціонування на старті з урахуванням зсуву
        start_x, start_y = PATH[0]
        if len(PATH) > 1:
            p2_x, p2_y = PATH[1]
            seg_len = math.hypot(p2_x - start_x, p2_y - start_y)
            if seg_len > 0:
                nx = -(p2_y - start_y) / seg_len
                ny = (p2_x - start_x) / seg_len
                start_x += nx * self.lane_offset
                start_y += ny * self.lane_offset
        self.x, self.y = start_x, start_y
        
        personal_speed_variance = random.uniform(0.9, 1.15)
        wave_hp_factor = (1.0 if wave == 1 else (1.0 + (wave - 1) * 0.55)) * 1.05

        if self.type == "normal":
            self.max_hp = max(1, int((18 + wave * 4.5) * wave_hp_factor))
            self.base_speed = 1.75 * speed_modifier * personal_speed_variance
            self.color = (240, 80, 80)
            self.reward = max(1, int(4 * reward_modifier))
            self.radius = 42
            self.damage_to_base = 6
        elif self.type == "fast":
            self.max_hp = max(1, int((12 + wave * 3.0) * wave_hp_factor))
            self.base_speed = 3.25 * speed_modifier * personal_speed_variance
            self.color = (255, 160, 40)
            self.reward = max(1, int(5 * reward_modifier))
            self.radius = 36
            self.damage_to_base = 4
        elif self.type == "tank":
            self.max_hp = max(1, int((58 + wave * 15) * wave_hp_factor))
            self.base_speed = 0.9 * speed_modifier * personal_speed_variance
            self.color = (160, 60, 180)
            self.reward = max(1, int(12 * reward_modifier))
            self.radius = 52
            self.damage_to_base = 22
        elif self.type == "scout":
            self.max_hp = max(1, int((10 + wave * 2.2) * wave_hp_factor))
            self.base_speed = 4.35 * speed_modifier * personal_speed_variance
            self.color = (240, 240, 50)
            self.reward = max(1, int(6 * reward_modifier))
            self.radius = 34
            self.damage_to_base = 3
        elif self.type == "bigyn":
            self.max_hp = max(1, int((160 + wave * 55) * wave_hp_factor))
            self.base_speed = 5.6 * speed_modifier * personal_speed_variance
            self.color = (255, 60, 120)
            self.reward = max(1, int(35 * reward_modifier))
            self.radius = 45
            self.damage_to_base = 50
        elif self.type == "boss":
            self.max_hp = max(1, int((160 + wave * 55) * wave_hp_factor))
            raw_spd = 1.75 if self.is_fast_boss else 1.3
            self.base_speed = raw_spd * speed_modifier * personal_speed_variance
            self.color = (200, 30, 30)
            self.reward = max(1, int(40 * reward_modifier))
            self.radius = 65
            self.damage_to_base = 50

        self.hp = self.max_hp
        self.speed = self.base_speed

    def take_damage(self, damage_amount):
        if self.hp <= 0:
            return 0
        actual_damage = min(self.hp, damage_amount)
        self.hp -= actual_damage
        
        earned_reward_fraction = (actual_damage / self.max_hp) * self.reward
        self.pending_reward_fraction += earned_reward_fraction
        
        gold_payout = int(self.pending_reward_fraction)
        self.pending_reward_fraction -= gold_payout
        return gold_payout

    def move(self):
        if self.slow_timer > 0:
            self.speed = self.base_speed * 0.7
            self.slow_timer -= 1
        else:
            self.speed = self.base_speed

        self.wander_phase += self.wander_speed
        dynamic_wave = math.sin(self.wander_phase) * 10.0

        if self.target_idx < len(PATH):
            p1_x, p1_y = PATH[self.target_idx - 1]
            p2_x, p2_y = PATH[self.target_idx]
            
            # Вектор поточного сегмента стежки
            seg_dx, seg_dy = p2_x - p1_x, p2_y - p1_y
            seg_len = math.hypot(seg_dx, seg_dy)
            if seg_len == 0: seg_len = 1
            
            # Нормаль (перпендикуляр) для зсуву вліво/вправо по всій ширині стежки
            nx = -seg_dy / seg_len
            ny = seg_dx / seg_len
            
            total_offset = self.lane_offset + dynamic_wave
            target_x = p2_x + nx * total_offset
            target_y = p2_y + ny * total_offset
            
            dx, dy = target_x - self.x, target_y - self.y
            dist = math.hypot(dx, dy)
            if dist == 0: dist = 1
            
            if dx > 0:
                self.facing_right = True
            elif dx < 0:
                self.facing_right = False

            if dist < self.speed:
                self.x, self.y = target_x, target_y
                self.target_idx += 1
            else:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
            return False
        return True

    def draw(self, surface):
        sh_w = int(self.radius * 1.5)
        sh_h = int(self.radius * 0.5)
        shadow_surf = pygame.Surface((sh_w, sh_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 55), (0, 0, sh_w, sh_h))
        surface.blit(shadow_surf, (int(self.x) - sh_w // 2, int(self.y) + self.radius // 3))

        img_set = ENEMY_IMAGES.get(self.type)
        if img_set:
            img = img_set["normal"] if self.facing_right else img_set["flipped"]
            img_x = int(self.x) - img.get_width() // 2
            img_y = int(self.y) - img.get_height() // 2
            surface.blit(img, (img_x, img_y))
        else:
            pygame.draw.circle(surface, (20, 20, 20), (int(self.x), int(self.y)), self.radius + 2)
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        
        if self.hp > 0:
            health_bar_width = self.radius * 2
            health_ratio = max(0, self.hp / self.max_hp)
            rx, ry = int(self.x) - self.radius, int(self.y) - self.radius - 12
            pygame.draw.rect(surface, (40, 10, 10), (rx, ry, health_bar_width, 6), border_radius=2)
            pygame.draw.rect(surface, (40, 220, 100), (rx, ry, int(health_bar_width * health_ratio), 6), border_radius=2)

class Tower:
    def __init__(self, x, y, tower_type, range_modifier, lvl_modifier=1.0):
        self.x = x
        self.y = y
        self.type = tower_type  
        self.level = 1
        self.cooldown = 0
        self.facing_left = True  
        
        self.click_radius = TOWER_BASE_SIZE[0] // 2
        
        if self.type == "rifleman":
            self.base_range = 135
            self.max_cooldown = 23
            self.damage = 4
            self.color = COLOR_RIFLEMAN
        elif self.type == "grenadier":
            self.base_range = 150
            self.max_cooldown = 40
            self.damage = 13
            self.color = COLOR_GRENADIER
        elif self.type == "gatling":
            self.base_range = 140
            self.max_cooldown = 14
            self.damage = 4
            self.color = COLOR_GATLING
        elif self.type == "cannon":
            self.base_range = 215
            self.max_cooldown = 32
            self.damage = 75
            self.color = COLOR_CANNON

        self.cost = int(BASE_TOWER_COSTS[self.type] * lvl_modifier)
        self.range = int(self.base_range * range_modifier)
        self.upgrade_cost = int(self.cost * 1.2)
        self.total_invested = self.cost

    def update_range(self, range_modifier):
        self.range = int(self.base_range * range_modifier)

    def upgrade(self, range_modifier):
        self.level += 1
        self.base_range += 12
        self.range = int(self.base_range * range_modifier)
        self.total_invested += self.upgrade_cost
        self.upgrade_cost = int(self.upgrade_cost * 1.5)
        
        if self.type == "rifleman":
            self.damage = int(self.damage * 1.45) + 1
            self.max_cooldown = max(12, int(self.max_cooldown * 0.9))
        elif self.type == "grenadier":
            self.damage = int(self.damage * 1.5) + 1
            self.max_cooldown = max(20, int(self.max_cooldown * 0.92))
        elif self.type == "gatling":
            self.damage = self.damage + 2
            self.max_cooldown = max(8, int(self.max_cooldown * 0.9))
        elif self.type == "cannon":
            self.damage = int(self.damage * 1.5) + 5
            self.max_cooldown = max(18, int(self.max_cooldown * 0.9))

    def shoot(self, enemies, bullets, explosions, particles):
        shot_fired = False
        in_range_enemies = [
            e for e in enemies 
            if e.hp > 0 and math.hypot(e.x - self.x, e.y - self.y) <= self.range
        ]
        
        target_enemy = None
        if in_range_enemies:
            if self.type in ["grenadier", "cannon"]:
                target_enemy = max(in_range_enemies, key=lambda e: e.hp)
            else:
                target_enemy = in_range_enemies[0]
                
        if target_enemy:
            self.facing_left = (target_enemy.x < self.x)
            
            if self.cooldown == 0:
                is_crit = (random.random() < 0.20)
                shot_damage = int(self.damage * 1.8) if is_crit else self.damage
                bullet_color = (255, 235, 70) if is_crit else self.color

                bullets.append(Bullet(self.x, self.y, target_enemy, shot_damage, self.type, bullet_color, is_crit=is_crit))
                self.cooldown = self.max_cooldown
                shot_fired = True

        if self.cooldown > 0:
            self.cooldown -= 1

        return shot_fired

    def draw(self, surface, is_selected=False, alpha=255):
        if is_selected:
            range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
            fill_a = int(30 * (alpha / 255))
            stroke_a = int(90 * (alpha / 255))
            pygame.draw.circle(range_surface, (100, 150, 255, fill_a), (self.range, self.range), self.range)
            pygame.draw.circle(range_surface, (100, 150, 255, stroke_a), (self.range, self.range), self.range, 1)
            surface.blit(range_surface, (self.x - self.range, self.y - self.range))
        
        img_set = TOWER_IMAGES[self.type]
        img = img_set["normal"] if self.facing_left else img_set["flipped"]
        img_x = self.x - img.get_width() // 2
        img_y = self.y - img.get_height() // 2
        surface.blit(img, (img_x, img_y))

        # Охайний текст рівня з чіткою піксельною обвідкою (без грубого бейджа)
        ry = self.y - TOWER_BASE_SIZE[1] // 2 + 5
        lvl_str = f"Lvl {self.level}"
        
        # Малюємо темний контур навколо літер для бездоганної видимості
        shadow_surf = FONT.render(lvl_str, True, (15, 20, 26))
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            surface.blit(shadow_surf, (self.x - shadow_surf.get_width() // 2 + ox, ry + oy))
            
        lvl_text = FONT.render(lvl_str, True, GOLD_COLOR)
        surface.blit(lvl_text, (self.x - lvl_text.get_width() // 2, ry))

class Bullet:
    def __init__(self, x, y, target, damage, bullet_type, color, is_crit=False):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.type = bullet_type
        self.color = color
        self.is_crit = is_crit
        
        if bullet_type == "cannon":
            self.speed = 15
        elif bullet_type == "gatling":
            self.speed = 12
        else:
            self.speed = 8

    def move(self, enemies, explosions, particles, flashes):
        if self.target not in enemies or self.target.hp <= 0:
            return True, 0

        dx, dy = self.target.x - self.x, self.target.y - self.y
        dist = math.hypot(dx, dy)
        gold_earned = 0
        
        if dist < self.speed:
            if self.is_crit:
                for _ in range(6):
                    particles.append(Particle(self.target.x, self.target.y, (255, 230, 80)))

            if self.type == "grenadier":
                ex_radius = 65
                explosions.append(Explosion(self.target.x, self.target.y, ex_radius))
                for _ in range(10):
                    particles.append(Particle(self.target.x, self.target.y, self.color))
                
                hit_enemies = [
                    e for e in enemies 
                    if e.hp > 0 and math.hypot(e.x - self.target.x, e.y - self.target.y) <= ex_radius
                ]
                for e in hit_enemies:
                    gold_earned += e.take_damage(self.damage)

            elif self.type == "cannon":
                cannon_radius = 80
                flashes.append(FlashEffect(self.target.x, self.target.y))
                for _ in range(14):
                    particles.append(Particle(self.target.x, self.target.y, (240, 200, 255)))
                
                hit_enemies = [
                    e for e in enemies 
                    if e.hp > 0 and math.hypot(e.x - self.target.x, e.y - self.target.y) <= cannon_radius
                ]
                for e in hit_enemies:
                    gold_earned += e.take_damage(self.damage)
            else:
                gold_earned += self.target.take_damage(self.damage)
                if self.type == "gatling":
                    self.target.slow_timer = 30
            return True, gold_earned
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        return False, gold_earned

class Explosion:
    def __init__(self, x, y, max_radius):
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.current_radius = 10
        self.speed = 6

    def draw(self, surface):
        if self.current_radius < self.max_radius:
            alpha = int(255 * (1 - self.current_radius / self.max_radius))
            exp_surface = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(exp_surface, (255, 100, 30, alpha), (self.max_radius, self.max_radius), int(self.current_radius))
            pygame.draw.circle(exp_surface, (255, 230, 150, alpha), (self.max_radius, self.max_radius), int(self.current_radius * 0.7), 2)
            surface.blit(exp_surface, (self.x - self.max_radius, self.y - self.max_radius))
            self.current_radius += self.speed
            return False
        return True

async def show_main_menu():
    menu_running = True
    while menu_running:
        screen.fill(BG_COLOR)
        mx, my = pygame.mouse.get_pos()
        
        title_surf = FONT_TITLE.render("БОЙОВІ ЇЖАЧКИ", True, TEXT_COLOR)
        subtitle_surf = FONT_LARGE.render("Тактичний Рубіж", True, ABILITY_COLOR)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 3 - 40))
        screen.blit(subtitle_surf, (WIDTH // 2 - subtitle_surf.get_width() // 2, HEIGHT // 3 + 25))
        
        start_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 65)
        is_hovered = start_rect.collidepoint(mx, my)
        btn_color = (38, 143, 85) if is_hovered else (28, 103, 61)
        
        pygame.draw.rect(screen, btn_color, start_rect, border_radius=12)
        pygame.draw.rect(screen, ABILITY_COLOR if is_hovered else PATH_BORDER, start_rect, 2, border_radius=12)
        
        btn_text = FONT_LARGE.render("СТАРТ ГРИ", True, TEXT_COLOR)
        screen.blit(btn_text, (start_rect.centerx - btn_text.get_width() // 2, start_rect.centery - btn_text.get_height() // 2))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_hovered:
                    menu_running = False
                    
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    return True

async def show_level_up_screen(next_lvl):
    for alpha in range(0, 160, 5):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 12, 20, alpha))
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        await asyncio.sleep(0.01)

    lvl_text = FONT_TITLE.render("ЗМІНА РІВНЯ", True, ABILITY_COLOR)
    sub_text = FONT_LARGE.render(f"Завантаження карти {next_lvl} з 5...", True, TEXT_COLOR)
    
    screen.blit(lvl_text, (WIDTH // 2 - lvl_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.flip()
    
    await asyncio.sleep(2.0)

def generate_wave_queue(wave_num, fast_boss_wave):
    queue = []
    
    if wave_num == 8:
        bigyns_count = 2
    elif wave_num == 9:
        bigyns_count = 3
    elif wave_num >= 10:
        bigyns_count = 4
    else:
        bigyns_count = 0

    if wave_num <= 3:
        normals = 5 + wave_num * 2
        scouts = 3 + wave_num * 2
        fasts = wave_num * 2
        items = ["normal"] * normals + ["scout"] * scouts + ["fast"] * fasts
        random.shuffle(items)
        queue = [(item, False) for item in items]
        
    elif wave_num <= 6:
        normals = 6 + wave_num
        scouts = 4 + wave_num
        fasts = 4 + wave_num
        tanks = wave_num - 2
        
        items = ["tank"] * tanks + ["normal"] * normals + ["fast"] * fasts + ["scout"] * scouts
        sub_items = items[2:]
        random.shuffle(sub_items)
        items = items[:2] + sub_items
        queue = [(item, False) for item in items]
        
    elif wave_num == 7:
        normals = 6 + wave_num
        scouts = 5 + wave_num
        fasts = 6 + wave_num
        tanks = wave_num - 3
        bosses = 1
        
        items = ["tank"] * 2 + ["normal"] * normals + ["boss"] * bosses + ["fast"] * fasts + ["scout"] * scouts + ["tank"] * (tanks - 2)
        random.shuffle(items)
        queue = [(item, False) for item in items]

    elif wave_num in [8, 9]:
        normals = 6 + wave_num
        scouts = 5 + wave_num
        fasts = 6 + wave_num
        tanks = max(1, wave_num - 3)
        bosses = 1 if wave_num == 8 else 2
        
        base_items = ["tank"] * 2 + ["normal"] * normals + ["boss"] * bosses + ["fast"] * fasts + ["scout"] * scouts + ["tank"] * (tanks - 2)
        random.shuffle(base_items)
        
        if bigyns_count > 0:
            step = len(base_items) // (bigyns_count + 1)
            for i in range(bigyns_count):
                idx = (i + 1) * step + i
                base_items.insert(idx, "bigyn")
        
        fast_boss_assigned = False
        for item in base_items:
            is_fast = False
            if item == "boss" and wave_num == fast_boss_wave and not fast_boss_assigned:
                is_fast = True
                fast_boss_assigned = True
            queue.append((item, is_fast))
        
    else:  # 10 штурм
        bosses = 3
        base_items = ["tank"] * 5 + ["normal"] * 12 + ["boss"] * bosses + ["fast"] * 10 + ["scout"] * 12 + ["tank"] * 4
        random.shuffle(base_items)
        base_items = ["tank", "tank"] + base_items
        
        if bigyns_count > 0:
            step = len(base_items) // (bigyns_count + 1)
            for i in range(bigyns_count):
                idx = (i + 1) * step + i
                base_items.insert(idx, "bigyn")
        
        fast_boss_assigned = False
        for item in base_items:
            is_fast = False
            if item == "boss" and wave_num == fast_boss_wave and not fast_boss_assigned:
                is_fast = True
                fast_boss_assigned = True
            queue.append((item, is_fast))
        
    return queue

async def main():
    global PATH, current_level
    
    if not await show_main_menu():
        return

    gold = 150
    lives = 100  
    wave = 1
    
    fast_boss_wave = random.choice([9, 10])
    
    current_wave_earned = 0
    level_gold_earned = 0
    level_completed = False
    
    enemies = []
    towers = []
    bullets = []
    explosions = []
    particles = []
    flashes = []
    
    BG_GRASS_SURFACE = generate_grass_background("forest_tileset.png", WIDTH, HEIGHT, tile_size=80)
    level_objects = spawn_environment(PATH, level_num=current_level)
    
    spawn_queue = [] 
    spawn_timer = 0
    next_spawn_delay = 0  
    wave_in_progress = False
    selected_tower = None
    
    SOLID_FRAMES = 180
    FADE_FRAMES = 90
    MAX_TOWER_TIMER = SOLID_FRAMES + FADE_FRAMES
    selected_tower_timer = 0
    
    current_build_type = "rifleman" 
    
    repair_base_cost = 32
    wave_timer_active = True
    wave_timer_counter = 20 * 60  
    
    speed_mod, reward_mod, range_mod = 1.0, 1.0, 1.0
    
    event_text_lines = ["Підготуйте їжачків до атаки!", "Таймер активовано."]
    
    ui_y_trigger = HEIGHT - 110
    btn_width = 135  
    start_btn_width = 240  
    
    prev_lvl_rect = pygame.Rect(15, ui_y_trigger + 8, 110, 24)
    next_lvl_rect = pygame.Rect(135, ui_y_trigger + 8, 115, 24)
    repair_btn_rect = pygame.Rect(840, ui_y_trigger + 45, 170, 50)
    
    panel_w, panel_h = 320, 95
    panel_x = WIDTH - panel_w - 15  
    panel_y = ui_y_trigger + 8
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    running = True
    while running:
        # 1. Трава
        screen.blit(BG_GRASS_SURFACE, (0, 0))
        mx, my = pygame.mouse.get_pos()
        time_sec = pygame.time.get_ticks() / 1000.0

        level_price_modifier = 1.0 + (current_level - 1) * 0.25
        PATH = LEVELS[current_level]

        panel_alpha = 255
        if selected_tower:
            if panel_rect.collidepoint(mx, my):
                selected_tower_timer = MAX_TOWER_TIMER
                panel_alpha = 255
            else:
                selected_tower_timer -= 1
                if selected_tower_timer <= 0:
                    selected_tower = None
                    panel_alpha = 0
                elif selected_tower_timer > FADE_FRAMES:
                    panel_alpha = 255
                else:
                    panel_alpha = max(0, min(255, int(255 * (selected_tower_timer / FADE_FRAMES))))

        # 2. Стежка
        if len(PATH) > 1:
            for point in PATH:
                pygame.draw.circle(screen, PATH_BORDER, point, 118 // 2)
            pygame.draw.lines(screen, PATH_BORDER, False, PATH, 118)
            
            for point in PATH:
                pygame.draw.circle(screen, PATH_COLOR, point, 102 // 2)
            pygame.draw.lines(screen, PATH_COLOR, False, PATH, 102)

            pygame.draw.lines(screen, PATH_INNER_LINE, False, PATH, 4)

        if wave_timer_active and not wave_in_progress and wave <= 10:
            wave_timer_counter -= 1
            if wave_timer_counter <= 0:
                current_wave_earned = 0
                PATH = LEVELS[current_level]
                spawn_queue = generate_wave_queue(wave, fast_boss_wave)
                wave_in_progress = True
                wave_timer_active = False
                next_spawn_delay = random.randint(10, 30)
                
                if wave > 3:
                    roll = random.random()
                    if roll < 0.5:
                        event_text_lines = ["ІВЕНТ: Золота лихоманка", "(Нагорода х2!)"]
                        speed_mod, reward_mod, range_mod = 1.0, 2.0, 1.0
                    else:
                        event_text_lines = ["ІВЕНТ: Попутна буря", "(Вороги прискорені)"]
                        speed_mod, reward_mod, range_mod = 1.3, 1.2, 1.0
                else:
                    speed_mod, reward_mod, range_mod = 1.0, 1.0, 1.0
                    event_text_lines = [f"Штурм {wave} почався!"]
                
                for t in towers: t.update_range(range_mod)

        if level_completed:
            btn_lvl_w, btn_lvl_h = 240, 50
            prev_lvl_active_rect = pygame.Rect(WIDTH // 2 - btn_lvl_w - 30, ui_y_trigger + 30, btn_lvl_w, btn_lvl_h)
            next_lvl_active_rect = pygame.Rect(WIDTH // 2 + 30, ui_y_trigger + 30, btn_lvl_w, btn_lvl_h)
        else:
            prev_lvl_active_rect = prev_lvl_rect
            next_lvl_active_rect = next_lvl_rect

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if level_completed:
                    if prev_lvl_active_rect.collidepoint(mx, my) and current_level > 1:
                        current_level -= 1
                        PATH = LEVELS[current_level]
                        enemies.clear()
                        bullets.clear()
                        towers.clear()
                        explosions.clear()
                        particles.clear()
                        flashes.clear()
                        selected_tower = None
                        spawn_queue = []
                        wave = 1
                        fast_boss_wave = random.choice([9, 10])
                        current_wave_earned = 0
                        level_gold_earned = 0
                        level_completed = False
                        repair_base_cost = 32
                        wave_timer_counter = 20 * 60
                        wave_timer_active = True
                        event_text_lines = ["Повернулись на", f"рівень {current_level}"]
                        level_objects = spawn_environment(PATH, level_num=current_level)
                        await show_level_up_screen(current_level)
                        continue

                    if next_lvl_active_rect.collidepoint(mx, my) and current_level < 5:
                        current_level += 1
                        PATH = LEVELS[current_level]
                        enemies.clear()
                        bullets.clear()
                        towers.clear()
                        explosions.clear()
                        particles.clear()
                        flashes.clear()
                        selected_tower = None
                        spawn_queue = []
                        wave = 1
                        fast_boss_wave = random.choice([9, 10])
                        current_wave_earned = 0
                        level_gold_earned = 0
                        level_completed = False
                        repair_base_cost = 32
                        wave_timer_counter = 20 * 60
                        wave_timer_active = True
                        event_text_lines = ["Ви перейшли на", f"рівень {current_level}"]
                        level_objects = spawn_environment(PATH, level_num=current_level)
                        await show_level_up_screen(current_level)
                        continue
                elif my < ui_y_trigger:  
                    clicked_tower = None
                    for t in towers:
                        if math.hypot(t.x - mx, t.y - my) < t.click_radius:
                            clicked_tower = t
                            break
                    
                    if clicked_tower:
                        selected_tower = clicked_tower
                        selected_tower_timer = MAX_TOWER_TIMER
                    else:
                        if is_on_path(mx, my, PATH, min_distance=85):
                            event_text_lines = ["Не можна ставити", "їжачків на дорогу!"]
                        elif len(towers) >= MAX_TOWERS:
                            event_text_lines = [f"Максимум їжачків: {MAX_TOWERS}!", "Оновлюйте старі."]
                        else:
                            on_tree_trunk = any(
                                o.type == "tree" and math.hypot(mx - o.x, my - o.y) < 55 
                                for o in level_objects
                            )
                            too_close_to_tower = any(math.hypot(mx - t.x, my - t.y) < 70 for t in towers)

                            if on_tree_trunk:
                                event_text_lines = ["Не ставте на стовбур!", "Ставте позаду дерева."]
                            elif not too_close_to_tower:
                                temp_tower = Tower(mx, my, current_build_type, range_mod, level_price_modifier)
                                if gold >= temp_tower.cost and selected_tower is None:
                                    towers.append(temp_tower)
                                    gold -= temp_tower.cost
                                    
                                    tower_names_ua = {
                                        "rifleman": "Автоматник",
                                        "grenadier": "Гранатометник",
                                        "gatling": "Кулеметник",
                                        "cannon": "Гарматник"
                                    }
                                    current_name_ua = tower_names_ua.get(current_build_type, current_build_type)
                                    event_text_lines = ["Придбано:", current_name_ua]
                        selected_tower = None

                else:  
                    if prev_lvl_rect.collidepoint(mx, my) and current_level > 1 and not wave_in_progress:
                        current_level -= 1
                        PATH = LEVELS[current_level]
                        enemies.clear()
                        bullets.clear()
                        towers.clear()
                        explosions.clear()
                        particles.clear()
                        flashes.clear()
                        selected_tower = None
                        spawn_queue = []
                        wave = 1
                        fast_boss_wave = random.choice([9, 10])
                        current_wave_earned = 0
                        level_gold_earned = 0
                        level_completed = False
                        repair_base_cost = 32
                        wave_timer_counter = 20 * 60
                        wave_timer_active = True
                        event_text_lines = ["Повернулись на", f"рівень {current_level}"]
                        level_objects = spawn_environment(PATH, level_num=current_level)
                        await show_level_up_screen(current_level)
                        continue

                    if next_lvl_rect.collidepoint(mx, my) and current_level < 5 and not wave_in_progress:
                        current_level += 1
                        PATH = LEVELS[current_level]
                        enemies.clear()
                        bullets.clear()
                        towers.clear()
                        explosions.clear()
                        particles.clear()
                        flashes.clear()
                        selected_tower = None
                        spawn_queue = []
                        wave = 1
                        fast_boss_wave = random.choice([9, 10])
                        current_wave_earned = 0
                        level_gold_earned = 0
                        level_completed = False
                        repair_base_cost = 32
                        wave_timer_counter = 20 * 60
                        wave_timer_active = True
                        event_text_lines = ["Ви перейшли на", f"рівень {current_level}"]
                        level_objects = spawn_environment(PATH, level_num=current_level)
                        await show_level_up_screen(current_level)
                        continue

                    if 15 <= mx <= 15 + start_btn_width and ui_y_trigger + 45 <= my <= ui_y_trigger + 95 and not wave_in_progress and wave <= 10 and not level_completed:
                        current_wave_earned = 0
                        PATH = LEVELS[current_level]
                        spawn_queue = generate_wave_queue(wave, fast_boss_wave)
                            
                        wave_in_progress = True
                        wave_timer_active = False
                        next_spawn_delay = random.randint(10, 30)
                        
                        if wave > 3:
                            roll = random.random()
                            if roll < 0.5:
                                event_text_lines = ["ІВЕНТ: Золота лихоманка", "(Нагорода х2!)"]
                                speed_mod, reward_mod, range_mod = 1.0, 2.0, 1.0
                            else:
                                event_text_lines = ["ІВЕНТ: Попутна буря", "(Вороги прискорені)"]
                                speed_mod, reward_mod, range_mod = 1.3, 1.2, 1.0
                        else:
                            speed_mod, reward_mod, range_mod = 1.0, 1.0, 1.0
                            event_text_lines = [f"Штурм {wave} почався!"]
                        
                        for t in towers: t.update_range(range_mod)

                    if ui_y_trigger + 45 <= my <= ui_y_trigger + 95:
                        if 270 <= mx <= 270 + btn_width: current_build_type = "rifleman"
                        elif 410 <= mx <= 410 + btn_width: current_build_type = "grenadier"
                        elif 550 <= mx <= 550 + btn_width: current_build_type = "gatling"
                        elif 690 <= mx <= 690 + btn_width: current_build_type = "cannon"

                    if repair_btn_rect.collidepoint(mx, my):
                        if lives >= 100:
                            event_text_lines = ["База вже повністю", "відремонтована!"]
                        elif gold >= repair_base_cost:
                            gold -= repair_base_cost
                            lives = min(100, lives + 10)
                            repair_base_cost = int(repair_base_cost * 1.25)
                            event_text_lines = ["Базу частково", "відновлено!"]
                        else:
                            event_text_lines = ["Немає грошей", "на ремонт!"]

                    if selected_tower and not level_completed:
                        if (panel_x + 15) <= mx <= (panel_x + 155) and (ui_y_trigger + 45) <= my <= (ui_y_trigger + 80):
                            if gold >= selected_tower.upgrade_cost:
                                gold -= selected_tower.upgrade_cost
                                selected_tower.upgrade(range_mod)
                                selected_tower_timer = MAX_TOWER_TIMER
                        elif (panel_x + 165) <= mx <= (panel_x + 305) and (ui_y_trigger + 45) <= my <= (ui_y_trigger + 80):
                            gold += selected_tower.total_invested // 2
                            towers.remove(selected_tower)
                            selected_tower = None

        if wave_in_progress:
            spawn_timer += 1
            if len(spawn_queue) > 0 and spawn_timer > next_spawn_delay:
                next_enemy_type, is_fast_boss = spawn_queue.pop(0)
                enemies.append(Enemy(wave, next_enemy_type, speed_mod, reward_mod, is_fast_boss))
                spawn_timer = 0
                
                if next_enemy_type in ["scout", "fast", "bigyn"]:
                    next_spawn_delay = random.randint(10, 22)
                elif next_enemy_type == "tank":
                    next_spawn_delay = random.randint(40, 65)
                elif next_enemy_type == "boss":
                    next_spawn_delay = random.randint(60, 90)
                else:
                    next_spawn_delay = random.randint(20, 40)
            
            if len(spawn_queue) == 0 and len(enemies) == 0:
                wave_in_progress = False
                selected_tower = None
                
                for t in towers: t.update_range(1.0)
                
                if wave < 10:
                    wave += 1
                    wave_timer_counter = 15 * 60  
                    wave_timer_active = True
                    event_text_lines = ["Штурм відбито!", f"Підготовка до {wave}-го штурму"]
                else:
                    wave = 10
                    if not level_completed:
                        level_completed = True
                    event_text_lines = ["Рівень захищено!", "Усі 10 штурмів пройдено."]

        # Стрільба веж
        for tower in towers:
            if tower.shoot(enemies, bullets, explosions, particles):
                gold += 1
                current_wave_earned += 1
                level_gold_earned += 1

        # Рух пацюків
        for enemy in enemies[:]:
            leaked = enemy.move()
            if leaked:
                hp_ratio = max(0.1, enemy.hp / enemy.max_hp)
                actual_damage = int(enemy.damage_to_base * hp_ratio)
                lives -= max(1, actual_damage)  
                enemies.remove(enemy)
            elif enemy.hp <= 0:
                for _ in range(8):
                    particles.append(Particle(enemy.x, enemy.y, enemy.color))
                enemies.remove(enemy)

        # =========================================================================
        # ІЗОМЕТРИЧНЕ СОРТУВАННЯ (Y-SORT)
        # =========================================================================
        render_queue = []
        for obj in level_objects:
            render_queue.append((obj.y, "obj", obj))
        for t in towers:
            render_queue.append((t.y + 40, "tower", t))
        for e in enemies:
            render_queue.append((e.y, "enemy", e))

        render_queue.sort(key=lambda item: item[0])

        for _, item_type, entity in render_queue:
            if item_type == "obj":
                entity.draw(screen, time_sec)
            elif item_type == "tower":
                entity.draw(screen, (entity == selected_tower and not level_completed), alpha=panel_alpha if entity == selected_tower else 255)
            elif item_type == "enemy":
                entity.draw(screen)

        # Прев'ю встановлення вежі
        if not level_completed and selected_tower is None and my < ui_y_trigger:
            temp_specs = {
                "rifleman": (135, COLOR_RIFLEMAN),
                "grenadier": (150, COLOR_GRENADIER),
                "gatling": (140, COLOR_GATLING),
                "cannon": (215, COLOR_CANNON)
            }
            current_range, tower_specific_color = temp_specs.get(current_build_type, (135, (255, 255, 255)))
            current_range = int(current_range * range_mod)
            
            collision_path = is_on_path(mx, my, PATH, min_distance=85)
            limit_reached = len(towers) >= MAX_TOWERS
            on_trunk = any(o.type == "tree" and math.hypot(mx - o.x, my - o.y) < 55 for o in level_objects)
            
            if collision_path or limit_reached or on_trunk:
                indicator_color = (255, 50, 50)  
            else:
                indicator_color = tower_specific_color  
            
            preview_surface = pygame.Surface((current_range * 2, current_range * 2), pygame.SRCALPHA)
            pygame.draw.circle(preview_surface, (*indicator_color, 25), (current_range, current_range), current_range)
            pygame.draw.circle(preview_surface, (*indicator_color, 120), (current_range, current_range), current_range, 1)
            screen.blit(preview_surface, (mx - current_range, my - current_range))
            
            pygame.draw.circle(screen, indicator_color, (mx, my), TOWER_BASE_SIZE[0] // 2 + 4, 2)

        # Снаряди та спецефекти
        for bullet in bullets[:]:
            removed, earned = bullet.move(enemies, explosions, particles, flashes)
            gold += earned
            current_wave_earned += earned
            level_gold_earned += earned
            if removed:
                bullets.remove(bullet)
            else:
                bullet_size = 7 if bullet.type == "cannon" else 5
                pygame.draw.circle(screen, bullet.color, (int(bullet.x), int(bullet.y)), bullet_size)

        for explosion in explosions[:]:
            if explosion.draw(screen): explosions.remove(explosion)

        for flash in flashes[:]:
            if flash.update(): flashes.remove(flash)
            else: flash.draw(screen)

        for p in particles[:]:
            if p.update(): particles.remove(p)
            else: p.draw(screen)

        if lives <= 0:
            screen.fill((15, 15, 22))
            loss_text = FONT_LARGE.render("БАЗУ ВТРАЧЕНО! Відступаємо.", True, HEALTH_COLOR)
            screen.blit(loss_text, (WIDTH // 2 - loss_text.get_width() // 2, HEIGHT // 2 - 20))
            pygame.display.flip()
            await asyncio.sleep(3)
            running = False
            continue

        # --- ОФОРМЛЕННЯ UI ---
        pygame.draw.rect(screen, UI_BG, (0, ui_y_trigger, WIDTH, 110))
        pygame.draw.line(screen, BORDER_COLOR, (0, ui_y_trigger), (WIDTH, ui_y_trigger), 3)

        if level_completed:
            glow_surf = FONT_TITLE.render("РІВЕНЬ ПРОЙДЕНО!", True, (150, 255, 230))
            screen.blit(glow_surf, (WIDTH // 2 - glow_surf.get_width() // 2 - 1, (ui_y_trigger // 2) - glow_surf.get_height() // 2))
            screen.blit(glow_surf, (WIDTH // 2 - glow_surf.get_width() // 2 + 1, (ui_y_trigger // 2) - glow_surf.get_height() // 2))
            screen.blit(glow_surf, (WIDTH // 2 - glow_surf.get_width() // 2, (ui_y_trigger // 2) - glow_surf.get_height() // 2 - 1))
            screen.blit(glow_surf, (WIDTH // 2 - glow_surf.get_width() // 2, (ui_y_trigger // 2) - glow_surf.get_height() // 2 + 1))
            
            comp_surf = FONT_TITLE.render("РІВЕНЬ ПРОЙДЕНО!", True, (255, 255, 255))
            screen.blit(comp_surf, (WIDTH // 2 - comp_surf.get_width() // 2, (ui_y_trigger // 2) - comp_surf.get_height() // 2))

            if current_level > 1:
                is_h_prev = prev_lvl_active_rect.collidepoint(mx, my)
                pygame.draw.rect(screen, (38, 143, 85) if is_h_prev else (28, 70, 50), prev_lvl_active_rect, border_radius=8)
                pygame.draw.rect(screen, ABILITY_COLOR if is_h_prev else PATH_BORDER, prev_lvl_active_rect, 2, border_radius=8)
                txt_p = FONT_LARGE.render("< Попередній", True, TEXT_COLOR)
                screen.blit(txt_p, (prev_lvl_active_rect.centerx - txt_p.get_width() // 2, prev_lvl_active_rect.centery - txt_p.get_height() // 2))

            if current_level < 5:
                is_h_next = next_lvl_active_rect.collidepoint(mx, my)
                pygame.draw.rect(screen, (38, 143, 85) if is_h_next else (28, 103, 61), next_lvl_active_rect, border_radius=8)
                pygame.draw.rect(screen, ABILITY_COLOR if is_h_next else PATH_BORDER, next_lvl_active_rect, 2, border_radius=8)
                txt_n = FONT_LARGE.render("Наступний >", True, TEXT_COLOR)
                screen.blit(txt_n, (next_lvl_active_rect.centerx - txt_n.get_width() // 2, next_lvl_active_rect.centery - txt_n.get_height() // 2))

        else:
            if current_level > 1:
                pygame.draw.rect(screen, (45, 55, 75), prev_lvl_rect, border_radius=4)
                screen.blit(FONT.render("< Рівень", True, TEXT_COLOR), (23, ui_y_trigger + 12))
                
            if current_level < 5:
                pygame.draw.rect(screen, (45, 55, 75), next_lvl_rect, border_radius=4)
                screen.blit(FONT.render("Рівень >", True, TEXT_COLOR), (147, ui_y_trigger + 12))

            y_normal = ui_y_trigger + 12
            y_slash = ui_y_trigger + 6

            # 1. БЛОК: КАРТА ТА ШТУРМ
            bx1 = 260
            wave_label = FONT.render(f"Карта: {current_level}  Штурм: ", True, TEXT_COLOR)
            wave_current = FONT.render(str(wave), True, TEXT_COLOR)
            wave_slash = FONT_LARGE.render("/", True, TEXT_COLOR)
            wave_max = FONT.render("10", True, TEXT_COLOR) 

            screen.blit(wave_label, (bx1, y_normal))
            bx1 += wave_label.get_width()
            screen.blit(wave_current, (bx1, y_normal))
            bx1 += wave_current.get_width() + 2
            screen.blit(wave_slash, (bx1, y_slash))
            bx1 += wave_slash.get_width() + 2
            screen.blit(wave_max, (bx1, y_normal))

            # 2. БЛОК: ЗОЛОТО
            bx2 = 460
            gold_surf = FONT.render(f"Золото: {gold} $", True, GOLD_COLOR)
            screen.blit(gold_surf, (bx2, y_normal))

            # 3. БЛОК: ЗДОРОВ'Я БАЗИ
            bx3 = 620
            current_hp = max(0, lives)
            dynamic_base_color = get_base_hp_color(current_hp)
            
            label_surf = FONT.render("База: ", True, dynamic_base_color)
            left_num_surf = FONT.render(str(current_hp), True, dynamic_base_color)
            slash_surf = FONT_LARGE.render("/", True, dynamic_base_color)
            right_num_surf = FONT.render("100", True, dynamic_base_color)

            screen.blit(label_surf, (bx3, y_normal))
            bx3 += label_surf.get_width()
            screen.blit(left_num_surf, (bx3, y_normal))
            bx3 += left_num_surf.get_width() + 2
            screen.blit(slash_surf, (bx3, y_slash))
            bx3 += slash_surf.get_width() + 2
            screen.blit(right_num_surf, (bx3, y_normal))

            # 4. БЛОК: КІЛЬКІСТЬ ЇЖАЧКІВ
            bx4 = 830
            hedgehogs_label = FONT.render("Їжачки: ", True, ABILITY_COLOR)
            hedgehogs_current = FONT.render(str(len(towers)), True, ABILITY_COLOR)
            hedgehogs_slash = FONT_LARGE.render("/", True, TEXT_COLOR)
            hedgehogs_max = FONT.render(str(MAX_TOWERS), True, ABILITY_COLOR)

            screen.blit(hedgehogs_label, (bx4, y_normal))
            bx4 += hedgehogs_label.get_width()
            screen.blit(hedgehogs_current, (bx4, y_normal))
            bx4 += hedgehogs_current.get_width() + 2
            screen.blit(hedgehogs_slash, (bx4, y_slash))
            bx4 += hedgehogs_slash.get_width() + 2
            screen.blit(hedgehogs_max, (bx4, y_normal))

            # 5. БЛОК: ТЕКСТ ПОДІЙ
            bx5 = 1040
            y_offset = ui_y_trigger + 10
            for line in event_text_lines:
                screen.blit(FONT.render(line, True, TEXT_COLOR), (bx5, y_offset))
                y_offset += 18

            if not wave_in_progress:
                pygame.draw.rect(screen, (38, 143, 85), (15, ui_y_trigger + 45, start_btn_width, 50), border_radius=6)
                txt_surf = FONT.render(f"Штурм! (Атака через {wave_timer_counter // 60}с)", True, TEXT_COLOR)
                screen.blit(txt_surf, (15 + (start_btn_width - txt_surf.get_width()) // 2, ui_y_trigger + 61))
                
                current_max_ticks = 20 * 60 if wave == 1 else 15 * 60
                progress_w = int((wave_timer_counter / current_max_ticks) * start_btn_width)
                pygame.draw.rect(screen, ABILITY_COLOR, (15, ui_y_trigger + 90, max(0, progress_w), 4))
            else:
                pygame.draw.rect(screen, (40, 45, 55), (15, ui_y_trigger + 45, start_btn_width, 50), border_radius=6)
                txt_surf = FONT.render("Бій триває", True, (140, 150, 160))
                screen.blit(txt_surf, (15 + (start_btn_width - txt_surf.get_width()) // 2, ui_y_trigger + 61))

            builds = [
                ("Автоматник", f"{int(BASE_TOWER_COSTS['rifleman'] * level_price_modifier)}$", "rifleman", 270, COLOR_RIFLEMAN),
                ("Гранатометник", f"{int(BASE_TOWER_COSTS['grenadier'] * level_price_modifier)}$", "grenadier", 410, COLOR_GRENADIER),
                ("Кулеметник", f"{int(BASE_TOWER_COSTS['gatling'] * level_price_modifier)}$", "gatling", 550, COLOR_GATLING),
                ("Гарматник", f"{int(BASE_TOWER_COSTS['cannon'] * level_price_modifier)}$", "cannon", 690, COLOR_CANNON)
            ]
            
            for name_str, price_str, t_id, bx, t_color in builds:
                is_active = (current_build_type == t_id)
                button_rect = pygame.Rect(bx, ui_y_trigger + 45, btn_width, 50)
                is_hovered = button_rect.collidepoint(mx, my)
                
                b_color = (24, 30, 41) if is_active else (24, 28, 38)
                pygame.draw.rect(screen, b_color, button_rect, border_radius=6)
                
                if is_hovered:
                    hover_surface = pygame.Surface((btn_width, 50), pygame.SRCALPHA)
                    pygame.draw.rect(hover_surface, (*t_color, 35), (0, 0, btn_width, 50), border_radius=6)
                    screen.blit(hover_surface, (bx, ui_y_trigger + 45))
                
                border_w = 3 if is_active else 1
                pygame.draw.rect(screen, t_color, button_rect, border_w, border_radius=6)
                
                screen.blit(FONT.render(name_str, True, TEXT_COLOR), (bx + 12, ui_y_trigger + 51))
                screen.blit(FONT.render(price_str, True, GOLD_COLOR), (bx + 12, ui_y_trigger + 71))

            pygame.draw.rect(screen, (32, 45, 68), repair_btn_rect, border_radius=6)
            pygame.draw.rect(screen, HEALTH_COLOR, repair_btn_rect, 1, border_radius=6)
            screen.blit(FONT.render("Ремонт Бази (+10)", True, TEXT_COLOR), (850, ui_y_trigger + 51))
            screen.blit(FONT.render(f"Ціна: {repair_base_cost}$", True, GOLD_COLOR), (850, ui_y_trigger + 71))

            if selected_tower and panel_alpha > 0:
                tower_names_ua = {
                    "rifleman": "Автоматник",
                    "grenadier": "Гранатометник",
                    "gatling": "Кулеметник",
                    "cannon": "Гарматник"
                }
                current_name_ua = tower_names_ua.get(selected_tower.type, selected_tower.type)
                sell_price = selected_tower.total_invested // 2

                panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)

                pygame.draw.rect(panel_surface, (24, 32, 48), (0, 0, panel_w, panel_h), border_radius=6)
                pygame.draw.rect(panel_surface, ABILITY_COLOR, (0, 0, panel_w, panel_h), 1, border_radius=6)
                
                title_text = FONT.render(f"Обрано: {current_name_ua}", True, TEXT_COLOR)
                panel_surface.blit(title_text, (15, 12))
                
                btn_up_rect_local = pygame.Rect(15, 45, 140, 35)
                pygame.draw.rect(panel_surface, (190, 105, 15), btn_up_rect_local, border_radius=5)
                up_text = FONT.render(f"Покращити: {selected_tower.upgrade_cost}$", True, TEXT_COLOR)
                panel_surface.blit(up_text, (btn_up_rect_local.centerx - up_text.get_width() // 2, btn_up_rect_local.centery - up_text.get_height() // 2))
                
                btn_sell_rect_local = pygame.Rect(165, 45, 140, 35)
                pygame.draw.rect(panel_surface, (180, 40, 40), btn_sell_rect_local, border_radius=5)
                sell_text = FONT.render(f"Продати: {sell_price}$", True, TEXT_COLOR)
                panel_surface.blit(sell_text, (btn_sell_rect_local.centerx - sell_text.get_width() // 2, btn_sell_rect_local.centery - sell_text.get_height() // 2))

                panel_surface.set_alpha(panel_alpha)
                screen.blit(panel_surface, (panel_x, panel_y))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())