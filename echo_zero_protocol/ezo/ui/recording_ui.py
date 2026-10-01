
import math,pygame
from game.settings import SCREEN_WIDTH,SCREEN_HEIGHT,CYAN_DIM,WHITE,TEXT_COLOR,PANEL_BG,PURPLE
class RecordingUI:
    def __init__(s):
        s.ft=pygame.font.SysFont("consolas",20,bold=True);s.fsp=pygame.font.SysFont("consolas",14,bold=True)
        s.ftx=pygame.font.SysFont("consolas",16);s.fh=pygame.font.SysFont("consolas",13)
        s.active=False;s.rec=None
    def start(s,rec):s.active=True;s.rec=rec
    def handle_event(s,ev):
        if not s.active:return False
        if ev.type==pygame.KEYDOWN and ev.key in(pygame.K_e,pygame.K_RETURN,pygame.K_SPACE,pygame.K_ESCAPE):s.active=False;return True
        return False
    def draw(s,sf):
        if not s.active or not s.rec:return
        ov=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA);ov.fill((0,0,0,160));sf.blit(ov,(0,0))
        pw,ph=600,340;px=SCREEN_WIDTH//2-pw//2;py=SCREEN_HEIGHT//2-ph//2
        pn=pygame.Surface((pw,ph),pygame.SRCALPHA)
        pygame.draw.rect(pn,(*PANEL_BG,230),(0,0,pw,ph),border_radius=10)
        pygame.draw.rect(pn,(160,100,220,200),(0,0,pw,ph),2,border_radius=10)
        pygame.draw.line(pn,PURPLE,(15,0),(pw-15,0),2);sf.blit(pn,(px,py))
        lb=s.fh.render("◆ RECORDING FOUND",True,(160,100,220));sf.blit(lb,(px+20,py+14))
        ti=s.ft.render(s.rec.get("title","Unknown"),True,WHITE);sf.blit(ti,(px+20,py+38))
        sp=s.fsp.render(f"— {s.rec.get('speaker','UNKNOWN')}",True,CYAN_DIM);sf.blit(sp,(px+20,py+66))
        words=s.rec.get("text","").split();line="";cy=py+95
        for w in words:
            test=line+w+" "
            if s.ftx.size(test)[0]>pw-40:
                if line:r=s.ftx.render(line.strip(),True,TEXT_COLOR);sf.blit(r,(px+20,cy));cy+=s.ftx.get_linesize()
                line=w+" "
            else:line=test
        if line.strip():r=s.ftx.render(line.strip(),True,TEXT_COLOR);sf.blit(r,(px+20,cy))
        t=pygame.time.get_ticks()/1000.0;p=int(140+80*math.sin(t*2.5))
        h=s.fh.render("[E] Close",True,(p,p,p));sf.blit(h,(px+pw-h.get_width()-20,py+ph-28))
