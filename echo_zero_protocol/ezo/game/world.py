import random,math,pygame
from game.settings import (TILE_SIZE,TILE_FLOOR,TILE_WALL,TILE_DOOR,TILE_TERMINAL,
    TILE_MEDICAL,TILE_EXIT,TILE_RECORDING,TILE_COLORS,CYAN_DIM,DARK_BG,PURPLE,SCREEN_WIDTH,SCREEN_HEIGHT)
from game.levels import LEVEL_CH0,LEVEL_CH1

class World:
    def __init__(s,chapter=0):
        s.tile_map=[row[:]for row in(LEVEL_CH0 if chapter==0 else LEVEL_CH1)]
        s.chapter=chapter;s.rows=len(s.tile_map);s.cols=len(s.tile_map[0])if s.rows else 0
        s.width=s.cols*TILE_SIZE;s.height=s.rows*TILE_SIZE
        s.wall_rects=[];s.interactables=[];s.exit_zones=[];s._build()
        s._cache=pygame.Surface((s.width,s.height));s._cache.fill(DARK_BG);s._render_cache()
    def _build(s):
        for r,row in enumerate(s.tile_map):
            for c,tile in enumerate(row):
                rect=pygame.Rect(c*TILE_SIZE,r*TILE_SIZE,TILE_SIZE,TILE_SIZE)
                if tile==TILE_WALL:s.wall_rects.append(rect)
                elif tile==TILE_DOOR:s.wall_rects.append(rect);s.interactables.append({"type":"door","rect":rect,"row":r,"col":c,"open":False})
                elif tile==TILE_TERMINAL:s.interactables.append({"type":"terminal","rect":rect,"row":r,"col":c,"used":False})
                elif tile==TILE_MEDICAL:s.interactables.append({"type":"medical","rect":rect,"row":r,"col":c})
                elif tile==TILE_EXIT:s.exit_zones.append(rect);s.interactables.append({"type":"exit","rect":rect,"row":r,"col":c})
                elif tile==TILE_RECORDING:s.interactables.append({"type":"recording","rect":rect,"row":r,"col":c,"used":False})
    def _render_cache(s):
        for r,row in enumerate(s.tile_map):
            for c,tile in enumerate(row):
                x,y=c*TILE_SIZE,r*TILE_SIZE;color=TILE_COLORS.get(tile,TILE_COLORS[TILE_FLOOR])
                if tile==TILE_WALL:
                    pygame.draw.rect(s._cache,color,(x,y,TILE_SIZE,TILE_SIZE))
                    l=tuple(min(v+18,255)for v in color);d=tuple(max(v-12,0)for v in color)
                    pygame.draw.line(s._cache,l,(x,y),(x+TILE_SIZE,y))
                    pygame.draw.line(s._cache,d,(x,y+TILE_SIZE-1),(x+TILE_SIZE,y+TILE_SIZE-1))
                elif tile==TILE_DOOR:
                    pygame.draw.rect(s._cache,(50,40,18),(x,y,TILE_SIZE,TILE_SIZE))
                    pygame.draw.rect(s._cache,(80,65,20),(x+4,y+TILE_SIZE//2-2,TILE_SIZE-8,4))
                else:
                    pygame.draw.rect(s._cache,color,(x,y,TILE_SIZE,TILE_SIZE))
                    pygame.draw.rect(s._cache,(color[0]+4,color[1]+4,color[2]+6),(x,y,TILE_SIZE,TILE_SIZE),1)
                    cx,cy=x+TILE_SIZE//2,y+TILE_SIZE//2
                    if tile==TILE_TERMINAL:pygame.draw.circle(s._cache,CYAN_DIM,(cx,cy),6)
                    elif tile==TILE_MEDICAL:
                        pygame.draw.line(s._cache,(60,20,20),(cx-5,cy),(cx+5,cy),2)
                        pygame.draw.line(s._cache,(60,20,20),(cx,cy-5),(cx,cy+5),2)
                    elif tile==TILE_EXIT:pygame.draw.rect(s._cache,(30,60,30),(x+2,y+2,TILE_SIZE-4,TILE_SIZE-4));pygame.draw.polygon(s._cache,(60,180,60),[(cx,cy-8),(cx+8,cy+4),(cx-8,cy+4)])
                    elif tile==TILE_RECORDING:pygame.draw.circle(s._cache,(80,50,120),(cx,cy),5)
    def draw(s,sf,cam):
        sx,sy=cam.apply((0,0));sf.blit(s._cache,(sx,sy));t=pygame.time.get_ticks()/1000.0
        for o in s.interactables:
            if o["type"]=="terminal" and not o.get("used"):
                p=int(40+25*math.sin(t*3+o["col"]));cx,cy=o["rect"].centerx,o["rect"].centery;scx,scy=cam.apply((cx,cy))
                g=pygame.Surface((28,28),pygame.SRCALPHA);pygame.draw.circle(g,(0,p+100,p+130,70),(14,14),14)
                sf.blit(g,(int(scx)-14,int(scy)-14))
            elif o["type"]=="door" and not o["open"]:
                sr=cam.apply_rect(o["rect"]);p=int(30+15*math.sin(t*2))
                pygame.draw.rect(sf,(p+40,p+30,0),sr,2)
            elif o["type"]=="exit":
                cx,cy=o["rect"].centerx,o["rect"].centery;scx,scy=cam.apply((cx,cy));p=int(30+25*math.sin(t*2.5))
                g=pygame.Surface((TILE_SIZE+16,TILE_SIZE+16),pygame.SRCALPHA)
                pygame.draw.rect(g,(p+30,p+80,p+30,50),(0,0,TILE_SIZE+16,TILE_SIZE+16),border_radius=6)
                sf.blit(g,(int(scx)-TILE_SIZE//2-8,int(scy)-TILE_SIZE//2-8))
            elif o["type"]=="recording" and not o.get("used"):
                cx,cy=o["rect"].centerx,o["rect"].centery;scx,scy=cam.apply((cx,cy));p=int(30+20*math.sin(t*2+o["row"]))
                g=pygame.Surface((24,24),pygame.SRCALPHA);pygame.draw.circle(g,(p+80,p+40,p+100,60),(12,12),12)
                sf.blit(g,(int(scx)-12,int(scy)-12))
    def get_spawn_pos(s):
        for r,row in enumerate(s.tile_map):
            for c,tile in enumerate(row):
                if tile==TILE_MEDICAL:return(c*TILE_SIZE+TILE_SIZE//2,r*TILE_SIZE+TILE_SIZE//2)
        return(TILE_SIZE*3,TILE_SIZE*3)
    def open_door(s,o):
        o["open"]=True;r,c=o["row"],o["col"];s.tile_map[r][c]=TILE_FLOOR
        if o["rect"]in s.wall_rects:s.wall_rects.remove(o["rect"])
        x,y=c*TILE_SIZE,r*TILE_SIZE;color=TILE_COLORS[TILE_FLOOR]
        pygame.draw.rect(s._cache,color,(x,y,TILE_SIZE,TILE_SIZE))
        pygame.draw.rect(s._cache,(color[0]+4,color[1]+4,color[2]+6),(x,y,TILE_SIZE,TILE_SIZE),1)
    def get_nearby_interactable(s,pos,radius=60):
        px,py=pos
        for o in s.interactables:
            if math.hypot(px-o["rect"].centerx,py-o["rect"].centery)<radius:return o
        return None
    def check_exit_zone(s,pp):
        pr=pygame.Rect(pp[0]-10,pp[1]-10,20,20)
        return any(pr.colliderect(ez)for ez in s.exit_zones)
