
import math,pygame
from game.settings import SCREEN_WIDTH,SCREEN_HEIGHT,CYAN,CYAN_DIM,WHITE,TEXT_COLOR,TEXT_DIM,PANEL_BG
class DialogueUI:
    def __init__(s):
        s.fsp=pygame.font.SysFont("consolas",16,bold=True);s.ftx=pygame.font.SysFont("consolas",18)
        s.fch=pygame.font.SysFont("consolas",16);s.fhi=pygame.font.SysFont("consolas",12)
        s.active=False;s.speaker="";s.full="";s.disp="";s.ci=0;s.ct=0.0;s.cspd=0.03
        s.choices=[];s.sc=0;s.wfc=False;s.fin=False;s.result=None
    def start(s,spk,txt,choices=None):
        s.active=True;s.speaker=spk;s.full=txt;s.disp="";s.ci=0;s.ct=0.0
        s.choices=choices or[];s.sc=0;s.wfc=False;s.fin=False;s.result=None
    def handle_event(s,ev):
        if not s.active:return None
        if ev.type==pygame.KEYDOWN:
            if not s.fin:
                if ev.key in(pygame.K_e,pygame.K_RETURN,pygame.K_SPACE):s.disp=s.full;s.fin=True;s.wfc=bool(s.choices)
            elif s.wfc:
                if ev.key in(pygame.K_w,pygame.K_UP):s.sc=(s.sc-1)%len(s.choices)
                elif ev.key in(pygame.K_s,pygame.K_DOWN):s.sc=(s.sc+1)%len(s.choices)
                elif ev.key in(pygame.K_e,pygame.K_RETURN,pygame.K_SPACE):
                    c=s.choices[s.sc];s.result={"type":"choice","id":c.get("id",""),"text":c.get("text","")};s.active=False;return s.result
            else:
                if ev.key in(pygame.K_e,pygame.K_RETURN,pygame.K_SPACE):s.result={"type":"continue"};s.active=False;return s.result
        return None
    def update(s,dt):
        if not s.active or s.fin:return
        s.ct+=dt
        while s.ct>=s.cspd and s.ci<len(s.full):s.ct-=s.cspd;s.ci+=1;s.disp=s.full[:s.ci]
        if s.ci>=len(s.full):s.fin=True;s.wfc=bool(s.choices)
    def draw(s,sf):
        if not s.active:return
        t=pygame.time.get_ticks()/1000.0;ph=160 if not s.choices else 160+len(s.choices)*28+16
        py=SCREEN_HEIGHT-ph-20;px=60;pw=SCREEN_WIDTH-120
        pn=pygame.Surface((pw,ph),pygame.SRCALPHA)
        pygame.draw.rect(pn,(*PANEL_BG,220),(0,0,pw,ph),border_radius=8)
        pygame.draw.rect(pn,(*CYAN_DIM,160),(0,0,pw,ph),1,border_radius=8)
        pygame.draw.line(pn,CYAN,(12,0),(pw-12,0),2);sf.blit(pn,(px,py))
        ic="◈ "if s.speaker.upper()=="ECHO"else"◇ "
        sp=s.fsp.render(ic+s.speaker.upper(),True,CYAN);sf.blit(sp,(px+20,py+14))
        # wrap text
        words=s.disp.split();line="";cy=py+40
        for word in words:
            test=line+word+" "
            if s.ftx.size(test)[0]>pw-40:
                if line:r=s.ftx.render(line.strip(),True,TEXT_COLOR);sf.blit(r,(px+20,cy));cy+=s.ftx.get_linesize()
                line=word+" "
            else:line=test
        if line.strip():r=s.ftx.render(line.strip(),True,TEXT_COLOR);sf.blit(r,(px+20,cy))
        if s.wfc and s.choices:
            cy2=py+100
            for i,ch in enumerate(s.choices):
                sel=i==s.sc;pre="▸ "if sel else"  ";clr=WHITE if sel else TEXT_DIM
                tx=s.fch.render(pre+ch["text"],True,clr)
                if sel:
                    hl=pygame.Surface((tx.get_width()+12,tx.get_height()+4),pygame.SRCALPHA)
                    pygame.draw.rect(hl,(0,60,80,80),(0,0,hl.get_width(),hl.get_height()),border_radius=3)
                    sf.blit(hl,(px+18,cy2-2))
                sf.blit(tx,(px+24,cy2));cy2+=28
        if s.fin and not s.wfc:
            h=s.fhi.render("[E] Continue",True,CYAN_DIM);sf.blit(h,(px+pw-h.get_width()-20,py+ph-22))
