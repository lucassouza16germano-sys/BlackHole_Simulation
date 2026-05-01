import pygame
import math
import random
from pygame.math import Vector3

pygame.init()

W, H = 1200, 800
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

BLACK = (0, 0, 0)

cam = Vector3(0, 50, -420)
yaw = 0
pitch = 0
speed = 1.5
look_speed = 0.02

bh_pos = Vector3(0, 0, 0)
bh_mass = 12000

star = Vector3(260, 100, 520)

particles = []

for _ in range(18000):
    r = random.uniform(60, 340)
    particles.append({
        "a": random.random() * math.tau,
        "r": r,
        "h": random.uniform(-1.2, 1.2),
        "v": 0.001 + (1 / (r + 10)) * 0.02
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
    if p.z <= 1:
        return None
    f = 950 / p.z
    return int(W / 2 + p.x * f), int(H / 2 - p.y * f), p.z

def lens(x, y, bx, by, strength=1.0):

    dx = x - bx
    dy = y - by

    r2 = dx*dx + dy*dy + 1.0

    force = (bh_mass / (r2 * math.sqrt(r2))) * strength

    x += dx * force * 0.25
    y += dy * force * 0.25

    swirl = 1.0 / (r2 * 0.02 + 1)

    x += -dy * swirl * 0.9
    y += dx * swirl * 0.9

    return x, y


def draw_blackhole(bx, by):

    for i in range(100, 10, -5):
        pygame.draw.circle(screen, (5, 5, 15), (bx, by), i)

    pygame.draw.circle(screen, (180, 180, 220), (bx, by), 44, 2)
    pygame.draw.circle(screen, (20, 20, 30), (bx, by), 28, 2)
    pygame.draw.circle(screen, (0, 0, 0), (bx, by), 16)


def draw_disk(bx, by):

    for p in particles:

        r = p["r"]

        speed = 1.0 / math.sqrt(r + 5)

        p["a"] += p["v"] * speed * 120
        p["r"] -= 0.04 * speed * 90

        if p["r"] < 40:
            p["r"] = random.uniform(180, 320)
            p["a"] = random.random() * math.tau
            p["h"] = random.uniform(-1.0, 1.0)

        x = math.cos(p["a"]) * p["r"]
        z = math.sin(p["a"]) * p["r"]

        flatten = 1.0 - (r / 320)
        y = p["h"] * flatten * 150

        cam_p = to_camera(Vector3(x, y, z))
        pr = project(cam_p)

        if not pr:
            continue

        sx, sy, sz = pr

        sx, sy = lens(sx, sy, bx, by, 1.0)

        dx = sx - bx
        dy = sy - by

        if dx*dx + dy*dy < 700:
            continue

        heat = max(0, 255 - int(r * 0.6))

        col = (
            255,
            120 + heat // 3,
            40 + heat // 6
        )

        size = 2 if r < 120 else 1

        screen.fill(col, (int(sx), int(sy), size, size))

def draw_star(bx, by):

    p = to_camera(star)
    pr = project(p)

    if not pr:
        return

    sx, sy, sz = pr

    sx, sy = lens(sx, sy, bx, by, 2.5)

    dx = sx - bx
    dy = sy - by
    dist = math.sqrt(dx*dx + dy*dy)

    fade = min(1.0, dist / 320.0)

    for i in range(22, 4, -2):
        c = int(255 * fade)
        pygame.draw.circle(screen, (c, c, 180), (int(sx), int(sy)), i)

    if fade > 0.15:
        pygame.draw.circle(screen, (255, 255, 255), (int(sx), int(sy)), 3)

running = True
while running:

    dt = clock.tick(60) / 16

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    forward = Vector3(math.sin(yaw), 0, math.cos(yaw))
    right = Vector3(forward.z, 0, -forward.x)

    if keys[pygame.K_w]: cam += forward * speed * dt
    if keys[pygame.K_s]: cam -= forward * speed * dt
    if keys[pygame.K_a]: cam -= right * speed * dt
    if keys[pygame.K_d]: cam += right * speed * dt

    if keys[pygame.K_SPACE]: cam.y += speed * dt
    if keys[pygame.K_LSHIFT]: cam.y -= speed * dt

    if keys[pygame.K_LEFT]: yaw -= look_speed * dt
    if keys[pygame.K_RIGHT]: yaw += look_speed * dt
    if keys[pygame.K_UP]: pitch -= look_speed * dt
    if keys[pygame.K_DOWN]: pitch += look_speed * dt

    screen.fill(BLACK)

    bh_proj = project(to_camera(bh_pos))
    bx, by = (bh_proj[0], bh_proj[1]) if bh_proj else (W // 2, H // 2)

    draw_disk(bx, by)
    draw_star(bx, by)
    draw_blackhole(bx, by)

    pygame.display.flip()

pygame.quit()