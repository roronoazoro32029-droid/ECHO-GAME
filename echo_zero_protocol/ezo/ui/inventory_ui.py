
import math,pygame
from game.settings import (SCREEN_WIDTH,SCREEN_HEIGHT,CYAN,CYAN_DIM,WHITE,TEXT_COLOR,TEXT_DIM,PANEL_BG,PANEL_BORDER,RED,GREEN,YELLOW)
from systems.inventory import ITEM_DB
class InventoryUI:
    COLS=4;CS=72;CG=8
    def __init__(s):
        s.sel=0;s.ft=pygame.font.SysFont("consolas",30,bold=True);s.fi=pygame.font.SysFont("consolas",14)
        s.fd=pygame.font.SysFont("consolas",15);s.fh=pygame.font.SysFont("consolas",13)
        s.fc=pygame.font.SysFont("consolas",28,bold=True);s.fn=pygame.font.SysFont("consolas",12,bold=True)
        s.ov=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA);s.ov.fill((0,0,0,180))
    def handle_event(s,ev,inv,player):
        items=inv.get_items_list();cnt=max(len(items),1)
        if ev.type==pygame.KEYDOWN:
            if ev.key in(pygame.K_TAB,pygame.K_ESCAPE):return "close",None
            elif ev.key in(pygame.K_d,pygame.K_RIGHT):s.sel=(s.sel+1)%cnt
            elif ev.key in(pygame.K_a,pygame.K_LEFT):s.sel=(s.sel-1)%cnt
            elif ev.key in(pygame.K_s,pygame.K_DOWN):s.sel=min(s.sel+s.COLS,cnt-1)
            elif ev.key in(pygame.K_w,pygame.K_UP):s.sel=max(s.sel-s.COLS,0)
            elif ev.key==pygame.K_e:
                if items and 0<=s.sel<len(items):
                    msg=inv.use_item(items[s.sel][0],player)
                    if msg:return "use",msg
            elif ev.key==pygame.K_q:
                if items and 0<=s.sel<len(items):
                    iid,_=items[s.sel];inv.remove_item(iid)
                    s.sel=max(0,min(s.sel,len(inv.get_items_list())-1))
                    return "drop",f"Dropped {ITEM_DB[iid]['name']}."
        return None,None
    def draw(s,sf,inv,player):
        sf.blit(s.ov,(0,0));t=pygame.time.get_ticks()/1000.0
        ti=s.ft.render("INVENTORY",True,CYAN);sf.blit(ti,(SCREEN_WIDTH//2-ti.get_width()//2,40))
        items=inv.get_items_list();gw=s.COLS*(s.CS+s.CG)-s.CG;gx=SCREEN_WIDTH//2-gw//2-120;gy=100
        rn=max(1,(len(items)+s.COLS-1)//s.COLS);ph=rn*(s.CS+s.CG)+30;pw=gw+40
        pn=pygame.Surface((pw,ph),pygame.SRCALPHA)
        pygame.draw.rect(pn,(*PANEL_BG,200),(0,0,pw,ph),border_radius=8)
        sf.blit(pn,(gx-20,gy-15))
        for i,(iid,cnt) in enumerate(items):
            col=i%s.COLS;row=i//s.COLS;cx=gx+col*(s.CS+s.CG);cy=gy+row*(s.CS+s.CG)
            info=ITEM_DB.get(iid,{});w=s.CS;sel=i==s.sel
            bg=(0,int(25+12*math.sin(t*4))+30,int(25+12*math.sin(t*4))+50)if sel else(18,22,34)
            pygame.draw.rect(sf,bg,(cx,cy,w,w),border_radius=6)
            pygame.draw.rect(sf,CYAN if sel else PANEL_BORDER,(cx,cy,w,w),2 if sel else 1,border_radius=6)
            ic=s.fc.render(info.get("icon_symbol","?"),True,info.get("icon_color",(100,100,100)))
            sf.blit(ic,(cx+w//2-ic.get_width()//2,cy+w//2-ic.get_height()//2-2))
            if cnt>1:cn=s.fn.render(f"x{cnt}",True,WHITE);sf.blit(cn,(cx+w-cn.get_width()-4,cy+w-16))
            nm=s.fi.render(info.get("name",iid)[:10],True,WHITE if sel else TEXT_DIM)
            sf.blit(nm,(cx+w//2-nm.get_width()//2,cy+w-16))
        # detail
        dpx,dpy=gx+gw+60,gy;dpw,dph=280,200
        dp=pygame.Surface((dpw,dph),pygame.SRCALPHA)
        pygame.draw.rect(dp,(*PANEL_BG,200),(0,0,dpw,dph),border_radius=8);sf.blit(dp,(dpx,dpy))
        if items and s.sel<len(items):
            iid,cnt=items[s.sel];info=ITEM_DB.get(iid,{})
            nm=s.ft.render(info.get("name",iid),True,WHITE);sf.blit(nm,(dpx+16,dpy+12))
            qt=s.fd.render(f"Qty: {cnt}",True,TEXT_COLOR);sf.blit(qt,(dpx+16,dpy+50))
            ds=s.fd.render(info.get("desc",""),True,TEXT_COLOR);sf.blit(ds,(dpx+16,dpy+75))
            if info.get("usable"):h=s.fh.render("Press E to use",True,GREEN);sf.blit(h,(dpx+16,dpy+dph-28))
        # stats
        sx,sy=gx-20,gy+ph+20
        for i,(txt,c) in enumerate([(f"HP: {int(player.health)}/{player.max_health}",RED),(f"Energy: {int(player.energy)}/{player.max_energy}",CYAN),(f"Ammo: {player.ammo}/{player.max_ammo}",YELLOW)]):
            st=s.fd.render(txt,True,c);sf.blit(st,(sx,sy+i*20))
        h=s.fh.render("WASD Navigate · E Use · Q Drop · TAB Close",True,TEXT_DIM)
        sf.blit(h,(SCREEN_WIDTH//2-h.get_width()//2,SCREEN_HEIGHT-40))
