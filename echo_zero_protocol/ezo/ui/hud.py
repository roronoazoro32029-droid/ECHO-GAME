
import math,pygame
from game.settings import (SCREEN_WIDTH,SCREEN_HEIGHT,CYAN,CYAN_DIM,RED,RED_DIM,GREEN,GREEN_DIM,
    YELLOW,YELLOW_DIM,WHITE,TEXT_COLOR,TEXT_DIM,PANEL_BG,PANEL_BORDER)
class HUD:
    def __init__(s):
        s.font=pygame.font.SysFont("consolas",16);s.font_sm=pygame.font.SysFont("consolas",13)
        s.font_lg=pygame.font.SysFont("consolas",18,bold=True);s.font_prompt=pygame.font.SysFont("consolas",20,bold=True)
        s.objective="Find a way out of Medical Sector A.";s.interaction_prompt=None
        s.show_echo_message=False;s.echo_message="";s.echo_timer=0.0
        s.weapon_name="PULSE PISTOL";s.behavior_profile="";s.echo_trust=""
    def draw(s,sf,p):
        s._bars(sf,p);s._ammo(sf,p);s._obj(sf)
        if s.interaction_prompt:s._prompt(sf)
        if s.show_echo_message:s._echo(sf)
        s._hints(sf)
    def _bars(s,sf,p):
        x,y=20,SCREEN_HEIGHT-90;bw,bh=180,12;g=20
        pn=pygame.Surface((bw+40,80),pygame.SRCALPHA)
        pygame.draw.rect(pn,(*PANEL_BG,180),(0,0,bw+40,80),border_radius=6)
        pygame.draw.rect(pn,(*PANEL_BORDER,120),(0,0,bw+40,80),1,border_radius=6)
        sf.blit(pn,(x-10,y-10))
        s._bar(sf,x,y,bw,bh,p.health,p.max_health,RED,RED_DIM,"HP")
        s._bar(sf,x,y+g,bw,bh,p.energy,p.max_energy,CYAN,CYAN_DIM,"EN")
        s._bar(sf,x,y+g*2,bw,bh,p.stamina,p.max_stamina,GREEN,GREEN_DIM,"ST")
    def _bar(s,sf,x,y,w,h,cur,mx,c,dc,lb):
        l=s.font_sm.render(lb,True,TEXT_DIM);sf.blit(l,(x,y-1));bx=x+28
        pygame.draw.rect(sf,(15,18,28),(bx,y,w-28,h),border_radius=3)
        r=max(0,cur/mx);fw=int((w-28)*r)
        if fw>0:pygame.draw.rect(sf,dc,(bx,y,fw,h),border_radius=3);pygame.draw.rect(sf,c,(bx,y,fw,h//2),border_radius=2)
        pygame.draw.rect(sf,PANEL_BORDER,(bx,y,w-28,h),1,border_radius=3)
        t=s.font_sm.render(f"{int(cur)}",True,TEXT_COLOR);sf.blit(t,(bx+w-28+4,y-1))
    def _ammo(s,sf,p):
        x,y=SCREEN_WIDTH-180,SCREEN_HEIGHT-60
        pn=pygame.Surface((160,50),pygame.SRCALPHA)
        pygame.draw.rect(pn,(*PANEL_BG,180),(0,0,160,50),border_radius=6)
        pygame.draw.rect(pn,(*PANEL_BORDER,120),(0,0,160,50),1,border_radius=6)
        sf.blit(pn,(x-10,y-10))
        w=s.font_sm.render(s.weapon_name,True,TEXT_DIM);sf.blit(w,(x,y-2))
        a=s.font_lg.render(f"{p.ammo} / {p.max_ammo}",True,CYAN);sf.blit(a,(x,y+16))
    def _obj(s,sf):
        x,y=SCREEN_WIDTH-340,20
        pn=pygame.Surface((320,50),pygame.SRCALPHA)
        pygame.draw.rect(pn,(*PANEL_BG,160),(0,0,320,50),border_radius=6)
        pygame.draw.rect(pn,(*PANEL_BORDER,100),(0,0,320,50),1,border_radius=6)
        sf.blit(pn,(x-10,y-8))
        l=s.font_sm.render("OBJECTIVE",True,CYAN_DIM);sf.blit(l,(x,y))
        o=s.font.render(s.objective,True,TEXT_COLOR);sf.blit(o,(x,y+18))
    def _prompt(s,sf):
        t=pygame.time.get_ticks()/1000.0;a=int(180+60*math.sin(t*3))
        tx=s.font_prompt.render(s.interaction_prompt,True,CYAN)
        px,py=SCREEN_WIDTH//2-tx.get_width()//2,SCREEN_HEIGHT//2+60
        bg=pygame.Surface((tx.get_width()+24,tx.get_height()+12),pygame.SRCALPHA)
        pygame.draw.rect(bg,(*PANEL_BG,200),bg.get_rect(),border_radius=4)
        pygame.draw.rect(bg,(*CYAN_DIM,min(a,180)),bg.get_rect(),1,border_radius=4)
        sf.blit(bg,(px-12,py-6));sf.blit(tx,(px,py))
    def _echo(s,sf):
        cx,y=SCREEN_WIDTH//2,90
        l=s.font_sm.render("◈ ECHO",True,CYAN);m=s.font.render(s.echo_message,True,TEXT_COLOR)
        tw=max(l.get_width(),m.get_width())+40
        pn=pygame.Surface((tw,52),pygame.SRCALPHA)
        pygame.draw.rect(pn,(*PANEL_BG,200),(0,0,tw,52),border_radius=6)
        pygame.draw.rect(pn,(*CYAN_DIM,140),(0,0,tw,52),1,border_radius=6)
        sf.blit(pn,(cx-tw//2,y-6));sf.blit(l,(cx-l.get_width()//2,y));sf.blit(m,(cx-m.get_width()//2,y+20))
    def _hints(s,sf):
        h=s.font_sm.render("[M] Map  [TAB] Inventory  [F] Flashlight  [Q] EMP",True,TEXT_DIM)
        sf.blit(h,(SCREEN_WIDTH//2-h.get_width()//2,SCREEN_HEIGHT-20))
        y=20
        if s.behavior_profile:
            p=s.font_sm.render(f"Profile: {s.behavior_profile.upper()}",True,TEXT_DIM);sf.blit(p,(20,y));y+=16
        if s.echo_trust:
            t=s.font_sm.render(f"ECHO: {s.echo_trust}",True,CYAN_DIM);sf.blit(t,(20,y))
    def show_echo(s,msg,dur=4.0): s.echo_message=msg;s.show_echo_message=True;s.echo_timer=dur
    def update(s,dt):
        if s.show_echo_message: s.echo_timer-=dt; s.show_echo_message=s.echo_timer>0
