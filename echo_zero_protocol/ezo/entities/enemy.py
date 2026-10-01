
import math, pygame
from game.settings import TILE_SIZE, PATHFIND_INTERVAL, RED, TEXT_DIM
from ai.pathfinding import find_path

class Enemy:
    def __init__(self,x,y,radius,health,speed,color,etype="enemy"):
        self.pos=pygame.math.Vector2(x,y); self.radius=radius
        self.health=health; self.max_health=health; self.speed=speed
        self.color=color; self.enemy_type=etype; self.alive=True; self.angle=0.0
        self.stunned=False; self.stun_timer=0.0
        self.rect=pygame.Rect(x-radius,y-radius,radius*2,radius*2)
        self.path=[]; self.path_index=0; self.path_timer=0.0
        self.attack_cooldown=0.0; self.last_known_player_pos=None; self.alert_level=0.0
        self.fsm=None; self._sprite=None; self._build_sprite()
    def _build_sprite(self):
        sz=self.radius*2+10; self._sprite=pygame.Surface((sz,sz),pygame.SRCALPHA); c=sz//2
        pygame.draw.circle(self._sprite,self.color,(c,c),self.radius,2)
        dim=tuple(max(v//3,0) for v in self.color)
        pygame.draw.circle(self._sprite,dim,(c,c),self.radius-2)
        pygame.draw.circle(self._sprite,self.color,(c+self.radius//2,c),3)
    def update(self,dt,ctx):
        if not self.alive: return
        if self.stunned:
            self.stun_timer-=dt
            if self.stun_timer<=0: self.stunned=False
            return
        self.attack_cooldown=max(0,self.attack_cooldown-dt); self.path_timer-=dt
        if self.fsm: self.fsm.update(self,dt,ctx)
        self.rect.center=(int(self.pos.x),int(self.pos.y))
    def move_toward(self,target,dt,walls):
        dx,dy=target[0]-self.pos.x,target[1]-self.pos.y; d=math.hypot(dx,dy)
        if d<4: return True
        dx,dy=dx/d,dy/d; self.angle=math.atan2(dy,dx)
        nx,ny=self.pos.x+dx*self.speed*dt,self.pos.y+dy*self.speed*dt
        t=pygame.Rect(nx-self.radius,ny-self.radius,self.radius*2,self.radius*2)
        if not any(t.colliderect(w) for w in walls): self.pos.x=nx; self.pos.y=ny
        return False
    def follow_path(self,dt,walls):
        if not self.path or self.path_index>=len(self.path): return True
        if self.move_toward(self.path[self.path_index],dt,walls): self.path_index+=1
        return self.path_index>=len(self.path)
    def request_path(self,tm,goal,od=None):
        if self.path_timer>0: return
        self.path=find_path(tm,(self.pos.x,self.pos.y),goal,od); self.path_index=0; self.path_timer=PATHFIND_INTERVAL
    def face_toward(self,t):
        dx,dy=t[0]-self.pos.x,t[1]-self.pos.y
        if abs(dx)>0.1 or abs(dy)>0.1: self.angle=math.atan2(dy,dx)
    def take_damage(self,a): self.health-=a; self.alive=self.health>0
    def apply_stun(self,dur=3.0): self.stunned=True; self.stun_timer=dur
    def draw(self,surface,cam):
        if not self.alive: return
        sx,sy=cam.apply(self.pos)
        if sx<-60 or sx>surface.get_width()+60 or sy<-60 or sy>surface.get_height()+60: return
        if self.stunned and(pygame.time.get_ticks()//100)%2==0:
            g=pygame.Surface((self.radius*4,self.radius*4),pygame.SRCALPHA)
            pygame.draw.circle(g,(255,255,100,50),(self.radius*2,self.radius*2),self.radius*2)
            surface.blit(g,(int(sx)-self.radius*2,int(sy)-self.radius*2))
        ad=-math.degrees(self.angle); r=pygame.transform.rotate(self._sprite,ad)
        rect=r.get_rect(center=(int(sx),int(sy))); surface.blit(r,rect)
        l=30; ha=math.radians(25)
        for ao in(-ha,ha):
            ex,ey=sx+math.cos(self.angle+ao)*l,sy+math.sin(self.angle+ao)*l
            pygame.draw.line(surface,self.color,(int(sx),int(sy)),(int(ex),int(ey)),1)
        if self.health<self.max_health:
            bw=self.radius*2+8; bx,by=int(sx)-bw//2,int(sy)-self.radius-12
            pygame.draw.rect(surface,(20,20,30),(bx,by,bw,4))
            fw=int(bw*(self.health/self.max_health))
            pygame.draw.rect(surface,RED if self.health/self.max_health<0.4 else self.color,(bx,by,fw,4))
        if self.fsm:
            f=pygame.font.SysFont("consolas",10)
            lb=f.render(self.fsm.current_name.upper(),True,TEXT_DIM)
            surface.blit(lb,(int(sx)-lb.get_width()//2,int(sy)+self.radius+6))
