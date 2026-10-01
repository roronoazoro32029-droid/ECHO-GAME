
import math,pygame
from game.settings import SCREEN_WIDTH,SCREEN_HEIGHT,CYAN,WHITE,TEXT_DIM,PANEL_BG,PANEL_BORDER
class PauseMenu:
    ITEMS=["RESUME","SETTINGS","SAVE GAME","MAIN MENU"]
    def __init__(s):
        s.selected=0;s.ft=pygame.font.SysFont("consolas",42,bold=True);s.fi=pygame.font.SysFont("consolas",24)
        s.ov=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA);s.ov.fill((0,0,0,160))
    def handle_event(s,ev):
        if ev.type==pygame.KEYDOWN:
            if ev.key==pygame.K_ESCAPE:return "RESUME"
            if ev.key in(pygame.K_w,pygame.K_UP):s.selected=(s.selected-1)%len(s.ITEMS)
            elif ev.key in(pygame.K_s,pygame.K_DOWN):s.selected=(s.selected+1)%len(s.ITEMS)
            elif ev.key in(pygame.K_RETURN,pygame.K_SPACE):return s.ITEMS[s.selected]
        if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
            if hasattr(s,"_ir"):
                for i,r in enumerate(s._ir):
                    if r.collidepoint(ev.pos):return s.ITEMS[i]
        if ev.type==pygame.MOUSEMOTION and hasattr(s,"_ir"):
            for i,r in enumerate(s._ir):
                if r.collidepoint(ev.pos):s.selected=i;break
    def draw(s,sf):
        sf.blit(s.ov,(0,0));cx=SCREEN_WIDTH//2;t=pygame.time.get_ticks()/1000.0
        ti=s.ft.render("PAUSED",True,CYAN);sf.blit(ti,(cx-ti.get_width()//2,180))
        s._ir=[];sy=280;sp=52
        for i,item in enumerate(s.ITEMS):
            y=sy+i*sp;sel=i==s.selected;bw,bh=240,40;bx=cx-bw//2;by=y-bh//2
            s._ir.append(pygame.Rect(bx,by,bw,bh))
            if sel:
                p=int(20+10*math.sin(t*4));pygame.draw.rect(sf,(0,p+25,p+40),(bx,by,bw,bh),border_radius=4)
                pygame.draw.rect(sf,CYAN,(bx,by,bw,bh),2,border_radius=4)
                tx=s.fi.render(f"▸ {item}",True,WHITE)
            else:
                pygame.draw.rect(sf,PANEL_BORDER,(bx,by,bw,bh),1,border_radius=4)
                tx=s.fi.render(item,True,TEXT_DIM)
            sf.blit(tx,(cx-tx.get_width()//2,y-tx.get_height()//2))
