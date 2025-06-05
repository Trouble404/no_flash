import pygame
import random
import time
import math

# 初始化
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("No Flash FPS Practice (Press [M] for Settings)")
clock = pygame.time.Clock()

# 颜色
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
LIGHT_YELLOW = (255, 255, 153)
TRANSPARENT_FLASH = (255, 255, 204)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# 全局变量
font = pygame.font.SysFont("Arial", 24)
score = 0
shots_fired = 0
shots_missed = 0
bubbles = []

# 玩家视角变量
player_angle = 0
mouse_sensitivity = 0.2

# 闪光弹变量
flash_warning = False
flash_active = False
flash_timer = 0
flash_warning_time = 0.7
flash_duration = 1.5
last_flash_time = time.time()
flash_cooldown = random.randint(5, 10)
flash_angle = 0
flash_effect_cached = None
flash_result_message = ""
flash_success_count = 0
flash_total_count = 0
flash_grenade_pos = None
flash_grenade_vel = None

# 音效
try:
    shoot_sound = pygame.mixer.Sound("shoot.wav")
    hit_sound = pygame.mixer.Sound("hit.wav")
    flash_sound = pygame.mixer.Sound("flash.wav")
except:
    shoot_sound = hit_sound = flash_sound = None

class Bubble:
    def __init__(self):
        self.x = random.randint(50, 750)
        self.y = random.randint(50, 550)
        self.radius = 10
        self.grow_time = random.uniform(1.5, 3.0)
        self.spawn_time = time.time()
        self.color = RED if random.random() < 0.7 else GREEN

    def update(self):
        elapsed = time.time() - self.spawn_time
        if elapsed < self.grow_time:
            self.radius = 10 + int(40 * (elapsed / self.grow_time))
        else:
            self.radius = 50

    def is_expired(self):
        return time.time() - self.spawn_time > self.grow_time + 1

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius, 2)

def spawn_bubble():
    bubbles.append(Bubble())

def start_flash_warning():
    global flash_warning, flash_thrown_time, initial_mouse_x
    global flash_grenade_pos, flash_grenade_vel
    flash_warning = True
    flash_thrown_time = time.time()
    initial_mouse_x = pygame.mouse.get_pos()[0]
    # 从边缘生成飞行路径
    start_x = random.choice([0, screen.get_width()])
    start_y = random.randint(50, screen.get_height() - 100)
    flash_grenade_pos = [start_x, start_y]
    target_x, target_y = screen.get_width() // 2, 100
    dx = target_x - start_x
    dy = target_y - start_y
    distance = math.hypot(dx, dy)
    speed = 600  # pixels per second (加快飞行速度)
    flash_grenade_vel = [dx / distance * speed, dy / distance * speed]

def update_flash_grenade(dt):
    if flash_grenade_pos and flash_grenade_vel:
        flash_grenade_pos[0] += flash_grenade_vel[0] * dt
        flash_grenade_pos[1] += flash_grenade_vel[1] * dt

def trigger_flash():
    global flash_active, flash_warning, flash_timer, flash_effect_cached
    global flash_result_message, flash_success_count, flash_total_count
    flash_active = True
    flash_warning = False
    flash_timer = time.time()
    flash_total_count += 1
    flash_effect_cached = get_flash_effect()
    if flash_effect_cached == TRANSPARENT_FLASH:
        flash_result_message = "✔ Backflash Success"
        flash_success_count += 1
    else:
        flash_result_message = "✖ Flashed"
    if flash_sound:
        flash_sound.play()

def draw_flash_grenade():
    if flash_warning and flash_grenade_pos:
        pygame.draw.circle(screen, YELLOW, (int(flash_grenade_pos[0]), int(flash_grenade_pos[1])), 10)

def draw_stats():
    accuracy = (score / shots_fired * 100) if shots_fired > 0 else 0
    backflash_rate = (flash_success_count / flash_total_count * 100) if flash_total_count > 0 else 0
    angle_txt = font.render(f"View Angle: {int(player_angle)}°", True, WHITE)
    stats_txt = font.render(f"Hit: {score}  Miss: {shots_missed}  Shots: {shots_fired}  Accuracy: {accuracy:.1f}%", True, WHITE)
    backflash_txt = font.render(f"Backflash Success Rate: {backflash_rate:.1f}% ({flash_success_count}/{flash_total_count})", True, WHITE)
    screen.blit(angle_txt, (10, 10))
    screen.blit(stats_txt, (10, 40))
    screen.blit(backflash_txt, (10, 70))

def draw_flash_result():
    if flash_active:
        msg = font.render(flash_result_message, True, WHITE)
        rect = msg.get_rect(center=(400, 300))
        screen.blit(msg, rect)

def draw_crosshair():
    x, y = pygame.mouse.get_pos()
    pygame.draw.line(screen, WHITE, (x - 10, y), (x + 10, y), 1)
    pygame.draw.line(screen, WHITE, (x, y - 10), (x, y + 10), 1)

def draw_quit_button():
    rect = pygame.Rect(680, 10, 110, 40)
    pygame.draw.rect(screen, RED, rect, border_radius=8)
    txt = font.render("[Q] QUIT", True, WHITE)
    screen.blit(txt, (rect.x + 10, rect.y + 8))
    return rect

def update_view_angle(mx):
    global player_angle
    center_x = screen.get_width() / 2
    player_angle = (mx - center_x) * mouse_sensitivity
    player_angle %= 360

def get_flash_effect():
    current_mouse_x = pygame.mouse.get_pos()[0]
    screen_width = screen.get_width()
    delta = abs(current_mouse_x - initial_mouse_x)
    moved_off_screen = current_mouse_x <= 5 or current_mouse_x >= screen_width - 5
    if moved_off_screen and delta > screen_width * 0.4:
        return TRANSPARENT_FLASH
    else:
        return YELLOW

pygame.mouse.set_visible(True)
pygame.event.set_grab(False)
running = True
bubble_timer = 0
prev_time = time.time()

while running:
    current_time = time.time()
    dt = current_time - prev_time
    prev_time = current_time

    screen.fill(BLACK)
    mx, my = pygame.mouse.get_pos()
    update_view_angle(mx)

    if not flash_warning and not flash_active and current_time - last_flash_time > flash_cooldown:
        start_flash_warning()
        last_flash_time = current_time
        flash_cooldown = random.randint(6, 10)

    if flash_warning:
        update_flash_grenade(dt)
        if current_time - flash_thrown_time > flash_warning_time:
            trigger_flash()

    if flash_active:
        if flash_effect_cached:
            screen.fill(flash_effect_cached)
        draw_flash_result()
        if time.time() - flash_timer > flash_duration:
            flash_active = False
            flash_effect_cached = None  # 重置使泡泡恢复生成

    if flash_effect_cached != YELLOW:
        if time.time() - bubble_timer > 1:
            spawn_bubble()
            bubble_timer = time.time()

        for b in bubbles[:]:
            b.update()
            b.draw()
            if b.is_expired():
                bubbles.remove(b)

    draw_flash_grenade()
    draw_stats()
    draw_crosshair()
    quit_btn_rect = draw_quit_button()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_m:
                import tkinter as tk
                root = tk.Tk()
                root.title("Game Settings")
                root.geometry("400x300")

                def apply_settings():
                    global bubble_timer, flash_duration, flash_warning_time, flash_cooldown, mouse_sensitivity
                    try:
                        flash_duration = float(flash_duration_var.get())
                        flash_warning_time = float(flash_warning_var.get())
                        flash_cooldown = int(flash_cooldown_var.get())
                        mouse_sensitivity = float(sensitivity_var.get())
                        bubble_interval = float(bubble_interval_var.get())
                        bubble_timer = time.time() - bubble_interval
                    except Exception as e:
                        print("Invalid input:", e)
                    root.destroy()


                tk.Label(root, text="Bubble Interval (sec):").pack()
                bubble_interval_var = tk.StringVar(value="1.0")
                tk.Entry(root, textvariable=bubble_interval_var).pack()

                tk.Label(root, text="Flash Duration (sec):").pack()
                flash_duration_var = tk.StringVar(value=str(flash_duration))
                tk.Entry(root, textvariable=flash_duration_var).pack()

                tk.Label(root, text="Flash Warning Time (sec):").pack()
                flash_warning_var = tk.StringVar(value=str(flash_warning_time))
                tk.Entry(root, textvariable=flash_warning_var).pack()

                tk.Label(root, text="Flash Cooldown (sec):").pack()
                flash_cooldown_var = tk.StringVar(value="7")
                tk.Entry(root, textvariable=flash_cooldown_var).pack()

                tk.Label(root, text="Mouse Sensitivity:").pack()
                sensitivity_var = tk.StringVar(value=str(mouse_sensitivity))
                tk.Entry(root, textvariable=sensitivity_var).pack()

                tk.Button(root, text="Apply", command=apply_settings).pack(pady=10)
                root.mainloop()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if quit_btn_rect.collidepoint(x, y):
                running = False
            elif not flash_active or flash_effect_cached != YELLOW:
                shots_fired += 1
                if shoot_sound:
                    shoot_sound.play()
                for b in bubbles[:]:
                    dist = math.hypot(b.x - x, b.y - y)
                    if dist < b.radius:
                        bubbles.remove(b)
                        score += 1
                        if hit_sound:
                            hit_sound.play()
                        break
                else:
                    shots_missed += 1

    clock.tick(60)

pygame.quit()
