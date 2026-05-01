import pygame
import math
import random
from pygame.math import Vector3


pygame.init()
W, H = 1200, 800
screen = pygame.display.set_mode((W, H), pygame.DOUBLEBUF | pygame.HWSURFACE)
font = pygame.font.SysFont("Arial", 18, bold=True)
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
cam = Vector3(0, 80, -450)
yaw, pitch = 0, 0.2
speed = 3.0
bh_mass = 10000 

stars = [Vector3(random.uniform(-1500, 1500), random.uniform(-900, 900), random.uniform(400, 2000)) for _ in range(1200)]

N = 15000 
particles = []
for _ in range(N):
    r = random.uniform(90, 380)
    particles.append({
        "a": random.uniform(0, math.tau),
        "r": r,
        "v": random.uniform(0.001, 0.005),
        "h": random.uniform(-2.5, 2.5),
        "noise": random.uniform(0.8, 1.2), # Oscilação de brilho
        "drift": random.uniform(-0.05, 0.05) # Instabilidade orbital
    })


def get_projection(p):
    p_rel = p - cam
    cy, sy = math.cos(yaw), math.sin(yaw)
    x, z = cy * p_rel.x - sy * p_rel.z, sy * p_rel.x + cy * p_rel.z
    cp, sp = math.cos(pitch), math.sin(pitch)
    y, z = cp * p_rel.y - sp * z, sp * p_rel.y + cp * z
    if z <= 10: return None
    f = 1000 / z
    return (int(W/2 + x*f), int(H/2 - y*f), z)

def lens_effect(x, y, bx, by):
    dx, dy = x - bx, y - by
    dist_sq = dx*dx + dy*dy + 1
   
    bend = (bh_mass / dist_sq)**0.65
    nx = x + dx * bend * 0.45
    ny = y + dy * bend * 0.45
    angle = math.atan2(dy, dx)
    swirl = 35 / (math.sqrt(dist_sq) * 0.04 + 1)
    nx += math.cos(angle + 1.2) * swirl
    ny += math.sin(angle + 1.2) * swirl
    return int(nx), int(ny)

def draw_hud(temp_avg):
    
    pygame.draw.rect(screen, (30, 30, 30), (50, H-100, 300, 40))
   
    for i in range(296):
       
        hue = i / 296
        color = (int(255 * (1-hue)), int(100 * hue + 50), int(255 * hue))
        if i < (temp_avg / 10000) * 296: 
            pygame.draw.line(screen, color, (52+i, H-98), (52+i, H-62))
    
   
    txt = font.render(f"TEMP. DISCO: {int(temp_avg)} K", True, (255, 255, 255))
    screen.blit(txt, (50, H-130))
    pygame.draw.rect(screen, (200, 200, 200), (50, H-100, 300, 40), 2)

running = True
total_heat = 0

while running:
    dt = clock.tick(60) / 16.0
    screen.fill(BLACK)
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT: running = False

   
    keys = pygame.key.get_pressed()
    forward = Vector3(math.sin(yaw), 0, math.cos(yaw))
    right = Vector3(forward.z, 0, -forward.x)
    if keys[pygame.K_w]: cam += forward * speed * dt
    if keys[pygame.K_s]: cam -= forward * speed * dt
    if keys[pygame.K_a]: cam -= right * speed * dt
    if keys[pygame.K_d]: cam += right * speed * dt
    if keys[pygame.K_SPACE]: cam.y += speed * dt
    if keys[pygame.K_LSHIFT]: cam.y -= speed * dt
    if keys[pygame.K_LEFT]: yaw -= 0.03 * dt
    if keys[pygame.K_RIGHT]: yaw += 0.03 * dt
    if keys[pygame.K_UP]: pitch -= 0.02 * dt
    if keys[pygame.K_DOWN]: pitch += 0.02 * dt

    bh_p = get_projection(Vector3(0, 0, 0))
    bx, by = bh_p[0], bh_p[1] if bh_p else (W//2, H//2)

    draw_buffer = []
    current_frame_heat = 0
    particles_count = 0

  
    for s in stars:
        proj = get_projection(s)
        if proj:
            lx, ly = lens_effect(proj[0], proj[1], bx, by)
            if 0 <= lx < W and 0 <= ly < H:
                draw_buffer.append((proj[2], lx, ly, (220, 220, 255), 1))

   
    for p in particles:
  
        p["a"] += p["v"] * (300/p["r"])
        p["r"] -= 0.03 * dt 
        
        if p["r"] < 62:
            p["r"] = random.uniform(340, 380)
            p["a"] = random.uniform(0, math.tau)

        
        r_eff = p["r"] + math.sin(pygame.time.get_ticks()*0.001 * p["drift"]) * 5
        x_3d = math.cos(p["a"]) * r_eff
        z_3d = math.sin(p["a"]) * r_eff
        
        
        y_3d = p["h"] * (bh_mass / (r_eff**1.5 + 1)) * 0.8

        proj = get_projection(Vector3(x_3d, y_3d, z_3d))
        if proj:
            lx, ly = lens_effect(proj[0], proj[1], bx, by)
            if (lx-bx)**2 + (ly-by)**2 < 1200: continue 
            
           
            t_val = (1.0 - (p["r"] / 400)) * 9000 + 1000
            current_frame_heat += t_val
            particles_count += 1
            
           
            if t_val > 7500: 
                c = (200, 220, 255)
            elif t_val > 4500:
                c = (255, 180, 50)
            else: 
                c = (180, 40, 20)
            
       
            bright = p["noise"] * (0.8 + 0.2 * math.sin(pygame.time.get_ticks()*0.005))
            final_col = (min(255, int(c[0]*bright)), min(255, int(c[1]*bright)), min(255, int(c[2]*bright)))
            
            draw_buffer.append((proj[2], lx, ly, final_col, 2 if p["r"] < 180 else 1))

    
    draw_buffer.sort(key=lambda x: x[0], reverse=True)
    for _, x, y, col, size in draw_buffer:
        if 0 <= x < W and 0 <= y < H:
            if size > 1: screen.fill(col, (x, y, size, size))
            else: screen.set_at((x, y), col)

 
    avg_temp = current_frame_heat / max(1, particles_count)
    draw_hud(avg_temp)

    pygame.display.flip()

pygame.quit()