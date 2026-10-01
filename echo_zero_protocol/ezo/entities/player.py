
import math, pygame
from game.settings import (PLAYER_SPEED, PLAYER_SPRINT_MULT, PLAYER_SIZE,
    PLAYER_MAX_HEALTH, PLAYER_MAX_STAMINA, PLAYER_MAX_ENERGY,
    PLAYER_STAMINA_DRAIN, PLAYER_STAMINA_REGEN, CYAN, CYAN_DIM)

class Player:
    def __init__(self, x, y):
        self.pos=pygame.math.Vector2(x,y); self.vel=pygame.math.Vector2(0,0)
        self.radius=PLAYER_SIZE
        self.rect=pygame.Rect(x-self.radius,y-self.radius,self.radius*2,self.radius*2)
        self.health=PLAYER_MAX_HEALTH; self.max_health=PLAYER_MAX_HEALTH
        self.stamina=PLAYER_MAX_STAMINA; self.max_stamina=PLAYER_MAX_STAMINA
        self.energy=PLAYER_MAX_ENERGY; self.max_energy=PLAYER_MAX_ENERGY
        self.ammo=24; self.max_ammo=48
        self.sprinting=False; self.flashlight_on=False; self.alive=True; self.angle=0.0
        self._build_sprite()
    def _build_sprite(self):
        sz=self.radius*2+8; self.sprite=pygame.Surface((sz,sz),pygame.SRCALPHA); c=sz//2
        pygame.draw.circle(self.sprite,(30,50,70),(c,c),self.radius,2)
        pygame.draw.circle(self.sprite,(20,35,55),(c,c),self.radius-2)
        g=pygame.Surface((sz,sz),pygame.SRCALPHA)
        pygame.draw.circle(g,(0,180,220,40),(c,c),self.radius-4)
        self.sprite.blit(g,(0,0)); pygame.draw.circle(self.sprite,CYAN,(c,c),3)
    def update(self,dt,keys,mouse,cam,walls):
        sp=cam.apply(self.pos); dx,dy=mouse[0]-sp[0],mouse[1]-sp[1]
        self.angle=math.atan2(dy,dx)
        mv=pygame.math.Vector2(0,0)
        if keys[pygame.K_w]:mv.y-=1
        if keys[pygame.K_s]:mv.y+=1
        if keys[pygame.K_a]:mv.x-=1
        if keys[pygame.K_d]:mv.x+=1
        if mv.length_squared()>0: mv=mv.normalize()
        speed=PLAYER_SPEED
        self.sprinting=keys[pygame.K_LSHIFT] and self.stamina>0 and mv.length_squared()>0
        if self.sprinting: speed*=PLAYER_SPRINT_MULT; self.stamina=max(0,self.stamina-PLAYER_STAMINA_DRAIN*dt)
        else: self.stamina=min(self.max_stamina,self.stamina+PLAYER_STAMINA_REGEN*dt)
        self.vel=mv*speed
        nx=self.pos.x+self.vel.x*dt
        tr=pygame.Rect(nx-self.radius,self.pos.y-self.radius,self.radius*2,self.radius*2)
        if not any(tr.colliderect(w) for w in walls): self.pos.x=nx
        ny=self.pos.y+self.vel.y*dt
        tr=pygame.Rect(self.pos.x-self.radius,ny-self.radius,self.radius*2,self.radius*2)
        if not any(tr.colliderect(w) for w in walls): self.pos.y=ny
        self.rect.center=(int(self.pos.x),int(self.pos.y))
    def draw(self,surface,cam):
        sx,sy=cam.apply(self.pos)
        if self.flashlight_on: self._draw_fl(surface,sx,sy)
        ad=-math.degrees(self.angle); r=pygame.transform.rotate(self.sprite,ad)
        rect=r.get_rect(center=(int(sx),int(sy))); surface.blit(r,rect)
        ex,ey=sx+math.cos(self.angle)*36,sy+math.sin(self.angle)*36
        pygame.draw.line(surface,CYAN_DIM,(int(sx),int(sy)),(int(ex),int(ey)),1)
    def _draw_fl(self,s,sx,sy):
        from game.settings import FLASHLIGHT_RANGE,FLASHLIGHT_ANGLE
        cs=pygame.Surface(s.get_size(),pygame.SRCALPHA); pts=[(int(sx),int(sy))]
        ha=math.radians(FLASHLIGHT_ANGLE)
        for i in range(21):
            a=self.angle-ha+(2*ha)*i/20
            pts.append((int(sx+math.cos(a)*FLASHLIGHT_RANGE),int(sy+math.sin(a)*FLASHLIGHT_RANGE)))
        if len(pts)>=3: pygame.draw.polygon(cs,(255,255,200,18),pts)
        s.blit(cs,(0,0))
    def toggle_flashlight(self): self.flashlight_on=not self.flashlight_on
    def take_damage(self,a): self.health=max(0,self.health-a); self.alive=self.health>0
    def heal(self,a): self.health=min(self.max_health,self.health+a)
