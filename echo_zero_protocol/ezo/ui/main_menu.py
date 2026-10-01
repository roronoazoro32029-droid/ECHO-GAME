
import random,math,time,pygame
from game.settings import SCREEN_WIDTH,SCREEN_HEIGHT,DARK_BG,CYAN,CYAN_DIM,WHITE,TEXT_COLOR,TEXT_DIM,PANEL_BG,PANEL_BORDER

class _P:
    __slots__=("x","y","vx","vy","life","ml","sz","color")
    def __init__(s):s.reset()
    def reset(s):
        s.x=random.uniform(0,SCREEN_WIDTH);s.y=random.uniform(0,SCREEN_HEIGHT)
        s.vx=random.uniform(-8,8);s.vy=random.uniform(-15,-4)
        s.life=random.uniform(2,6);s.ml=s.life;s.sz=random.uniform(1,3)
        s.color=random.choice([(0,180,220),(0,120,160),(60,80,120)])
    def update(s,dt):
        s.x+=s.vx*dt;s.y+=s.vy*dt;s.life-=dt
        if s.life<=0 or s.y<-10:s.reset();s.y=SCREEN_HEIGHT+10
    def draw(s,sf):
        a=max(0,min(255,int(255*(s.life/s.ml)))); sz=max(1,int(s.sz*(s.life/s.ml)))
        if a>10:
            g=pygame.Surface((sz*4,sz*4),pygame.SRCALPHA)
            pygame.draw.circle(g,(*s.color,a//2),(sz*2,sz*2),sz*2)
            sf.blit(g,(int(s.x)-sz*2,int(s.y)-sz*2))
            pygame.draw.circle(sf,(*s.color,a),(int(s.x),int(s.y)),sz)

class MainMenu:
    ITEMS=["NEW GAME","CONTINUE","SETTINGS","EXIT"]
    def __init__(s,screen):
        s.screen=screen;s.selected=0;s.particles=[_P()for _ in range(80)]
        s.ft=pygame.font.SysFont("consolas",72,bold=True)
        s.fs=pygame.font.SysFont("consolas",22);s.fi=pygame.font.SysFont("consolas",28)
        s.fh=pygame.font.SysFont("consolas",14);s.st=time.time()
        s.scanlines=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
        for y in range(0,SCREEN_HEIGHT,3):pygame.draw.line(s.scanlines,(0,0,0,20),(0,y),(SCREEN_WIDTH,y))
    def handle_event(s,ev):
        if ev.type==pygame.KEYDOWN:
            if ev.key in(pygame.K_w,pygame.K_UP):s.selected=(s.selected-1)%len(s.ITEMS)
            elif ev.key in(pygame.K_s,pygame.K_DOWN):s.selected=(s.selected+1)%len(s.ITEMS)
            elif ev.key in(pygame.K_RETURN,pygame.K_SPACE):return s.ITEMS[s.selected]
        if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:return s._click(ev.pos)
        if ev.type==pygame.MOUSEMOTION:s._hover(ev.pos)
    def update(s,dt):
        for p in s.particles:p.update(dt)
    def draw(s):
        s.screen.fill(DARK_BG);t=time.time()-s.st;cx=SCREEN_WIDTH//2
        for x in range(0,SCREEN_WIDTH,60):pygame.draw.line(s.screen,(20,30,45),(x,0),(x,SCREEN_HEIGHT))
        for y in range(0,SCREEN_HEIGHT,60):pygame.draw.line(s.screen,(20,30,45),(0,y),(SCREEN_WIDTH,y))
        for p in s.particles:p.draw(s.screen)
        go=random.randint(-4,4)if random.random()<0.03 else 0
        ts=s.ft.render("ECHO",True,CYAN);gs=s.ft.render("ECHO",True,(0,80,100))
        s.screen.blit(gs,(cx-gs.get_width()//2+2+go,122));s.screen.blit(ts,(cx-ts.get_width()//2+go,120))
        ss=s.fs.render("Z E R O   P R O T O C O L",True,CYAN_DIM)
        s.screen.blit(ss,(cx-ss.get_width()//2,200))
        s._ir=[];sy=310;sp=56
        for i,item in enumerate(s.ITEMS):
            y=sy+i*sp;sel=i==s.selected;bw,bh=280,44;bx=cx-bw//2;by=y-bh//2
            s._ir.append(pygame.Rect(bx,by,bw,bh))
            if sel:
                p=int(20+10*math.sin(t*4))
                pygame.draw.rect(s.screen,(0,p+30,p+50),(bx,by,bw,bh),border_radius=4)
                pygame.draw.rect(s.screen,CYAN,(bx,by,bw,bh),2,border_radius=4)
                ar=s.fi.render("▸ ",True,CYAN);tx=s.fi.render(item,True,WHITE)
                tw=ar.get_width()+tx.get_width()
                s.screen.blit(ar,(cx-tw//2,y-ar.get_height()//2))
                s.screen.blit(tx,(cx-tw//2+ar.get_width(),y-tx.get_height()//2))
            else:
                pygame.draw.rect(s.screen,PANEL_BORDER,(bx,by,bw,bh),1,border_radius=4)
                tx=s.fi.render(item,True,TEXT_DIM);s.screen.blit(tx,(cx-tx.get_width()//2,y-tx.get_height()//2))
        h=s.fh.render("↑↓ Navigate · ENTER Select · Python + Pygame",True,TEXT_DIM)
        s.screen.blit(h,(cx-h.get_width()//2,SCREEN_HEIGHT-40));s.screen.blit(s.scanlines,(0,0))
    def _click(s,pos):
        if not hasattr(s,"_ir"):return
        for i,r in enumerate(s._ir):
            if r.collidepoint(pos):s.selected=i;return s.ITEMS[i]
    def _hover(s,pos):
        if not hasattr(s,"_ir"):return
        for i,r in enumerate(s._ir):
            if r.collidepoint(pos):s.selected=i;break
