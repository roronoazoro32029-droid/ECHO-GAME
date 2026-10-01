
import math,pygame
from game.settings import SCREEN_WIDTH,SCREEN_HEIGHT,DARK_BG,CYAN,CYAN_DIM,TEXT_COLOR,TEXT_DIM
class ChapterIntroUI:
    def __init__(s):
        s.ft=pygame.font.SysFont("consolas",36,bold=True);s.fs=pygame.font.SysFont("consolas",20)
        s.fl=pygame.font.SysFont("consolas",17);s.fh=pygame.font.SysFont("consolas",14)
        s.active=False;s.data=None;s.timer=0.0;s.phase=0
    def start(s,d):s.active=True;s.data=d;s.timer=0.0;s.phase=0
    def handle_event(s,ev):
        if not s.active:return False
        if ev.type==pygame.KEYDOWN:
            if s.phase<2:s.phase=2;s.timer=0
            else:s.active=False;return True
        return False
    def update(s,dt):
        if not s.active:return
        s.timer+=dt
        if s.phase==0 and s.timer>2.0:s.phase=1;s.timer=0
        elif s.phase==1 and s.timer>4.0:s.phase=2;s.timer=0
    def draw(s,sf):
        if not s.active or not s.data:return
        sf.fill(DARK_BG);cx=SCREEN_WIDTH//2;t=pygame.time.get_ticks()/1000.0;f=min(1.0,s.timer/1.5)
        c=tuple(int(v*f)for v in CYAN);ts=s.ft.render(s.data.get("title",""),True,c)
        sf.blit(ts,(cx-ts.get_width()//2,200))
        if s.phase>=1:
            a=min(1.0,s.timer/1.0)if s.phase==1 else 1.0;sc=tuple(int(v*a)for v in TEXT_DIM)
            ss=s.fs.render(s.data.get("subtitle",""),True,sc);sf.blit(ss,(cx-ss.get_width()//2,250))
            for i,line in enumerate(s.data.get("lines",[])):
                dl=0.6*i;la=max(0,min(1.0,(s.timer-dl)/0.8))if s.phase==1 else 1.0
                lc=tuple(int(v*la)for v in TEXT_COLOR);ls=s.fl.render(line,True,lc)
                sf.blit(ls,(cx-ls.get_width()//2,310+i*28))
        if s.phase==2:
            p=int(120+80*math.sin(t*3));h=s.fh.render("Press any key to continue...",True,(p,p,p))
            sf.blit(h,(cx-h.get_width()//2,SCREEN_HEIGHT-60))

class EndingUI:
    def __init__(s):
        s.ft=pygame.font.SysFont("consolas",38,bold=True);s.fl=pygame.font.SysFont("consolas",18)
        s.fst=pygame.font.SysFont("consolas",15);s.fh=pygame.font.SysFont("consolas",14)
        s.active=False;s.ending=None;s.bdata=None;s.etrust=0;s.timer=0.0;s.done=False
    def start(s,e,bd,t):s.active=True;s.ending=e;s.bdata=bd;s.etrust=t;s.timer=0.0;s.done=False
    def handle_event(s,ev):
        if not s.active:return None
        if ev.type==pygame.KEYDOWN:
            if not s.done:s.done=True;s.timer=99
            else:s.active=False;return "main_menu"
    def update(s,dt):
        if not s.active:return
        s.timer+=dt;lines=s.ending.get("lines",[])if s.ending else[]
        if s.timer>1.0+len(lines)*0.4+2.0:s.done=True
    def draw(s,sf):
        if not s.active or not s.ending:return
        sf.fill(DARK_BG);cx=SCREEN_WIDTH//2;t=pygame.time.get_ticks()/1000.0
        tc=s.ending.get("color",CYAN);f=min(1.0,s.timer/1.5)
        c=tuple(int(v*f)for v in tc);ti=s.ft.render(s.ending["title"],True,c)
        sf.blit(ti,(cx-ti.get_width()//2,60))
        for i,line in enumerate(s.ending.get("lines",[])):
            dl=1.0+0.4*i;a=max(0,min(1.0,(s.timer-dl)/0.6))
            if a<=0 or line=="":continue
            lc=tuple(int(v*a)for v in TEXT_COLOR);ls=s.fl.render(line,True,lc)
            sf.blit(ls,(cx-ls.get_width()//2,130+i*26))
        sd=1.0+len(s.ending.get("lines",[]))*0.4+0.5;sa=max(0,min(1.0,(s.timer-sd)/1.0))
        if sa>0 and s.bdata:
            lc=tuple(int(v*sa)for v in CYAN_DIM);vc=tuple(int(v*sa)for v in TEXT_COLOR)
            sl=s.fst.render(s.ending.get("stats_label",""),True,lc);sf.blit(sl,(cx-sl.get_width()//2,530))
            stats=[f"Play Time: {int(s.bdata.get('play_time',0)//60)}m {int(s.bdata.get('play_time',0)%60)}s",
                f"Enemies Killed: {s.bdata.get('kills',0)}",f"Terminals: {s.bdata.get('terminals_accessed',0)}",
                f"Evidence Found: {s.bdata.get('evidence_found',0)}",f"ECHO Trust: {int(s.etrust)}%"]
            for i,st in enumerate(stats):r=s.fst.render(st,True,vc);sf.blit(r,(cx-r.get_width()//2,554+i*20))
        if s.done:
            p=int(120+80*math.sin(t*3));h=s.fh.render("Press any key to return to menu...",True,(p,p,p))
            sf.blit(h,(cx-h.get_width()//2,SCREEN_HEIGHT-40))
