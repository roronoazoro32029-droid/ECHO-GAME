
import math,random,pygame
from game.settings import MAX_PARTICLES

class Projectile:
    def __init__(s,x,y,angle,speed,damage,color,owner="player",size=4,lifetime=2.0):
        s.pos=pygame.math.Vector2(x,y)
        s.vel=pygame.math.Vector2(math.cos(angle)*speed,math.sin(angle)*speed)
        s.damage=damage;s.color=color;s.owner=owner;s.size=size;s.alive=True;s.lifetime=lifetime
    def update(s,dt,walls,tm=None):
        s.lifetime-=dt
        if s.lifetime<=0: s.alive=False; return
        s.pos+=s.vel*dt; r=s.size
        rect=pygame.Rect(s.pos.x-r,s.pos.y-r,r*2,r*2)
        for wr in walls:
            if rect.colliderect(wr): s.alive=False; return
    def draw(s,surface,cam):
        sx,sy=cam.apply(s.pos); ix,iy=int(sx),int(sy)
        g=pygame.Surface((s.size*6,s.size*6),pygame.SRCALPHA)
        pygame.draw.circle(g,(*s.color,40),(s.size*3,s.size*3),s.size*3)
        surface.blit(g,(ix-s.size*3,iy-s.size*3))
        pygame.draw.circle(surface,s.color,(ix,iy),s.size)
        pygame.draw.circle(surface,(255,255,255),(ix,iy),max(1,s.size-2))
        tx,ty=ix-s.vel.x*0.02,iy-s.vel.y*0.02
        pygame.draw.line(surface,s.color,(ix,iy),(int(tx),int(ty)),max(1,s.size-1))

class Particle:
    __slots__=("x","y","vx","vy","life","max_life","size","color","alive")
    def __init__(s,x,y,vx,vy,life,size,color):
        s.x=x;s.y=y;s.vx=vx;s.vy=vy;s.life=life;s.max_life=life;s.size=size;s.color=color;s.alive=True
    def update(s,dt):
        s.x+=s.vx*dt;s.y+=s.vy*dt;s.vx*=0.96;s.vy*=0.96;s.life-=dt;s.alive=s.life>0
    def draw(s,surface,cam):
        sx,sy=cam.apply((s.x,s.y)); a=max(0,int(255*(s.life/s.max_life)))
        sz=max(1,int(s.size*(s.life/s.max_life)))
        if a>10: pygame.draw.circle(surface,s.color,(int(sx),int(sy)),sz)

class ParticleManager:
    def __init__(s): s.particles=[]
    def update(s,dt):
        for p in s.particles: p.update(dt)
        s.particles=[p for p in s.particles if p.alive]
        if len(s.particles)>MAX_PARTICLES: s.particles=s.particles[-MAX_PARTICLES:]
    def draw(s,surface,cam):
        for p in s.particles: p.draw(surface,cam)
    def emit_sparks(s,x,y,color,count=8):
        import math,random
        for _ in range(count):
            a=random.uniform(0,math.pi*2);sp=random.uniform(60,200)
            s.particles.append(Particle(x,y,math.cos(a)*sp,math.sin(a)*sp,random.uniform(0.2,0.6),random.uniform(1,3),color))
    def emit_muzzle_flash(s,x,y,angle,color):
        import math,random
        for _ in range(5):
            sp=random.uniform(-0.3,0.3);spd=random.uniform(100,250);a=angle+sp
            s.particles.append(Particle(x,y,math.cos(a)*spd,math.sin(a)*spd,random.uniform(0.1,0.25),random.uniform(2,4),color))
        s.particles.append(Particle(x,y,0,0,0.08,8,(255,255,255)))
    def emit_explosion(s,x,y,color,count=20):
        import math,random
        for _ in range(count):
            a=random.uniform(0,math.pi*2);sp=random.uniform(40,180)
            s.particles.append(Particle(x,y,math.cos(a)*sp,math.sin(a)*sp,random.uniform(0.3,0.8),random.uniform(2,5),color))
    def emit_death(s,x,y,color): s.emit_explosion(x,y,color,25); s.emit_sparks(x,y,(255,255,200),10)
    def emit_emp(s,x,y,radius):
        import math
        for i in range(30):
            a=(i/30)*math.pi*2; sp=radius/0.4
            s.particles.append(Particle(x,y,math.cos(a)*sp,math.sin(a)*sp,0.4,3,(255,255,100)))
