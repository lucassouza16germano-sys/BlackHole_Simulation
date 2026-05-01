import pygame
import math
import random
from pygame.math import Vector3


pygame.init()
W, H = 1200, 800
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

cam = Vector3(0, 80, -500)
yaw, pitch = 0, 0
speed = 2.5

bh_pos = Vector3(0, 0, 0)
bh_mass = 12000 
horizon_radius = 45 

light_star = Vector3(400, 150, 600)


stars = [Vector3(random.uniform(-2000, 2000), random.uniform(-1500, 1500), random.uniform(500, 2000)) for _ in range(1200)]

N = 30000
particles = []
for _ in range(N):
    r = random.uniform(70, 450)
    particles.append({
        "a": random.uniform(0, math.tau),
        "r": r,
        "v": random.uniform(0.02, 0.08), 
        "h": random.uniform(-2.5, 2.5),
        "color_seed": random.random()
    })

def to_camera(p):
    p = p - cam
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    x = cy * p.x - sy * p.z
    z = sy * p.x + cy * p.z
    y = cp * p.y - sp * z
    z = sp * p.y + cp * z
    return Vector3(x, y, z)

def project(p):
    if p.z <= 1: return None
    f = 1000 / p.z
    return int(W/2 + p.x * f), int(H/2 - p.y * f), p.z

def lens_effect(sx, sy, bx, by, power=1.0):
    dx, dy = sx - bx, sy - by
    d2 = dx*dx + dy*dy + 0.1
    
    dist = math.sqrt(d2)
    factor = (bh_mass * power) / (dist + 0.1)
    
    nx = sx + (dx / dist) * factor
    ny = sy + (dy / dist) * factor
    return nx, ny

def draw_black_hole(bh_screen):
    
    pygame.draw.circle(screen, BLACK, (int(bh_screen[0]), int(bh_screen[1])), horizon_radius)
  
    pygame.draw.circle(screen, (30, 10, 5), (int(bh_screen[0]), int(bh_screen[1])), horizon_radius + 2, 2)

def draw_star_and_glow(bh_screen):
    p_star = to_camera(light_star)
    pr = project(p_star)
    if not pr: return
    
    bx, by = bh_screen
    sx, sy, sz = pr
    
    lx, ly = lens_effect(sx, sy, bx, by, 4.5)
    
    glow_size = max(1, int(4000 / sz))
    for i in range(glow_size, 1, -4):
        alpha_col = max(0, min(255, 255 - i*2))
        pygame.draw.circle(screen, (255, 230, 150), (int(lx), int(ly)), i)
    pygame.draw.circle(screen, WHITE, (int(lx), int(ly)), max(1, glow_size // 4))

def draw_scene():
    bh_proj = project(to_camera(bh_pos))
    if not bh_proj: return
    bx, by, bz = bh_proj
    
    for s in stars:
        p = to_camera(s)
        pr = project(p)
        if pr:
            x, y = lens_effect(pr[0], pr[1], bx, by, 0.5)
            screen.set_at((int(x), int(y)), (150, 150, 180))
    for p in particles:
     
        p["a"] += p["v"] * (150 / math.sqrt(p["r"]))
        
        x = math.cos(p["a"]) * p["r"]
        z = math.sin(p["a"]) * p["r"]
        y = p["h"] * math.sin(p["a"] * 0.5) 

        cp = to_camera(Vector3(x, y, z))
        pr = project(cp)
        
        if pr:
           
            lx, ly = lens_effect(pr[0], pr[1], bx, by, 1.2)
            
            dist_to_center = math.hypot(lx - bx, ly - by)
            if dist_to_center < horizon_radius - 5: continue

            temp = max(0, min(1, (p["r"] - 70) / 380))
            r_col = int(255)
            g_col = int(100 + 155 * temp)
            b_col = int(50 + 205 * (temp**2))
            
            screen.fill((r_col, g_col, b_col), (int(lx), int(ly), 1, 1))

    draw_star_and_glow((bx, by))
    draw_black_hole((bx, by))


running = True       
while running:
    dt = clock.tick(60) / 16.0
    for e in pygame.event.get():
        if e.type == pygame.QUIT: running = False

    keys = pygame.key.get_pressed()
    fwd = Vector3(math.sin(yaw), 0, math.cos(yaw))
    side = Vector3(fwd.z, 0, -fwd.x)
    
    if keys[pygame.K_w]: cam += fwd * speed * dt
    if keys[pygame.K_s]: cam -= fwd * speed * dt
    if keys[pygame.K_a]: cam -= side * speed * dt
    if keys[pygame.K_d]: cam += side * speed * dt
    if keys[pygame.K_LEFT]: yaw -= 0.03 * dt
    if keys[pygame.K_RIGHT]: yaw += 0.03 * dt
    if keys[pygame.K_UP]: pitch -= 0.03 * dt
    if keys[pygame.K_DOWN]: pitch += 0.03 * dt

    screen.fill(BLACK)
    draw_scene()
    pygame.display.flip()

pygame.quit()