import pygame
import math
import random
from pygame.math import Vector3

pygame.init() 
W,H=1200,800
screen=pygame.display.set_mode((W,H))
clock=pygame.time.Clock()

BLACK=(0,0,0)
WHITE=(255,255,255)

cam=Vector3(0,45,-360)
yaw=0
pitch=0
speed=1.5

bh_pos=Vector3(0,0,0)
bh_mass=8200

light_star=Vector3(190,80,420)

stars=[
    Vector3(random.uniform(-1000,1000),
            random.uniform(-700,700),
            random.uniform(250,1300))
    for _ in range(1600)
]

N=16000
particles=[]

for _ in range(N):
    r=random.uniform(100,320)
    particles.append({
        "a":random.uniform(0,math.tau),
        "r":r,
        "v":random.uniform(0.0009,0.0035),
        "h":random.uniform(-1.4,1.4),
  
        "layer":
            0 if r<160 else
            1 if r<240 else
            2
    })

def to_camera(p):
    p=p-cam
    cy,sy=math.cos(yaw),math.sin(yaw)
    cp,sp=math.cos(pitch),math.sin(pitch)

    x=cy*p.x - sy*p.z
    z=sy*p.x + cy*p.z
    y=cp*p.y - sp*z
    z=sp*p.y + cp*z

    return Vector3(x,y,z)

def project(p):
    if p.z<=1: return None
    f=920/p.z
    return int(W/2+p.x*f), int(H/2-p.y*f), p.z

def lens(x,y,bx,by,strength=1.0):

    dx=x-bx
    dy=y-by
    d2=dx*dx+dy*dy + 1

    bend=(bh_mass/d2)**0.58 * strength

    x+=dx*bend*0.32
    y+=dy*bend*0.32

    swirl=1.0/(math.sqrt(d2)*0.03+1)
    angle=math.atan2(dy,dx)

    x+=math.cos(angle+1.3)*swirl
    y+=math.sin(angle+1.3)*swirl

    return x,y

def draw_light_star(bh_screen):

    pr=project(to_camera(light_star))
    if not pr: return

    sx,sy,sz=pr

    sx,sy=lens(sx,sy,bh_screen[0],bh_screen[1],3.0)

  
    glow=max(3,int(18-sz*0.01))

    for i in range(glow,3,-2):
        pygame.draw.circle(screen,(255,255,190),(int(sx),int(sy)),i)

  
    pygame.draw.circle(screen,(255,255,255),(int(sx),int(sy)),3)


def draw_stars(bh_screen):
    bx,by=bh_screen
    for s in stars:
        p=to_camera(s)
        pr=project(p)
        if pr:
            x,y,_=pr
            x,y=lens(x,y,bx,by,0.9)
            screen.fill((255,255,255),(int(x),int(y),1,1))

def draw_disk(bh_screen):

    bx,by=bh_screen
    pts=[]

    for p in particles:

        r=p["r"]
        layer=p["layer"]

       
        layer_speed=[0.6,1.0,1.5][layer]

        p["a"]+=p["v"]*layer_speed*(260/r)
        p["r"]-=0.02*layer_speed

        if p["r"]<60:
            p["r"]=random.uniform(260,320)
            p["a"]=random.uniform(0,math.tau)
            p["h"]=random.uniform(-1.4,1.4)

        x=math.cos(p["a"])*p["r"]
        z=math.sin(p["a"])*p["r"]

        dist2=x*x+z*z
        bend=bh_mass/(dist2+1)

       
        flatten=1.0-(r/320)
        y=p["h"]*bend*150*flatten

        cam_p=to_camera(Vector3(x,y,z))
        pr=project(cam_p)

        if not pr:
            continue

        sx,sy,sz=pr

        sx,sy=lens(sx,sy,bx,by,1.0)

        dx=sx-bx
        dy=sy-by
        if dx*dx+dy*dy<1050:
            continue

        heat=255-int(r*1.0)
        heat=max(0,heat)

        col=(
            min(255,200+heat//4),
            min(255,120+heat//2),
            min(255,70+heat//3)
        )

        size=2 if layer==0 else 1

        pts.append((sz,sx,sy,col,size))

    for _,x,y,col,size in pts:
        screen.fill(col,(int(x),int(y),size,size))

running=True
while running:
    dt=clock.tick(60)/16

    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running=False

    keys=pygame.key.get_pressed()

    forward=Vector3(math.sin(yaw),0,math.cos(yaw))
    right=Vector3(forward.z,0,-forward.x)

    if keys[pygame.K_w]: cam+=forward*speed*dt
    if keys[pygame.K_s]: cam-=forward*speed*dt
    if keys[pygame.K_a]: cam-=right*speed*dt
    if keys[pygame.K_d]: cam+=right*speed*dt

    if keys[pygame.K_SPACE]: cam.y+=speed*dt
    if keys[pygame.K_LSHIFT]: cam.y-=speed*dt

    if keys[pygame.K_LEFT]: yaw-=0.02*dt
    if keys[pygame.K_RIGHT]: yaw+=0.02*dt
    if keys[pygame.K_UP]: pitch-=0.02*dt
    if keys[pygame.K_DOWN]: pitch+=0.02*dt

    screen.fill(BLACK)

    bh_proj=project(to_camera(bh_pos))
    if bh_proj:
        bh_screen=(bh_proj[0],bh_proj[1])
    else:
        bh_screen=(W//2,H//2)

    draw_stars(bh_screen)
    draw_disk(bh_screen)
    draw_light_star(bh_screen)

    pygame.display.flip()

pygame.quit()