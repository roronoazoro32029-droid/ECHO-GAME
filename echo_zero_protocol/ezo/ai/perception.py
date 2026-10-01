
import math
from game.settings import TILE_SIZE, TILE_WALL, TILE_DOOR

def has_line_of_sight(tm, fp, tp, od=None):
    dx,dy=tp[0]-fp[0],tp[1]-fp[1]; d=math.hypot(dx,dy)
    if d<1: return True
    steps=int(d/(TILE_SIZE*0.4))+1
    for i in range(1,steps):
        t=i/steps; px,py=fp[0]+dx*t,fp[1]+dy*t
        c,r=int(px//TILE_SIZE),int(py//TILE_SIZE)
        if r<0 or r>=len(tm) or c<0 or c>=len(tm[0]): return False
        tile=tm[r][c]
        if tile==TILE_WALL: return False
        if tile==TILE_DOOR and not(od and(r,c)in od): return False
    return True

def in_field_of_view(epos, eangle, tpos, half_deg, srange):
    dx,dy=tpos[0]-epos[0],tpos[1]-epos[1]; d=math.hypot(dx,dy)
    if d>srange: return False,d
    a=math.atan2(dy,dx); diff=abs((eangle-a+math.pi)%(2*math.pi)-math.pi)
    return diff<=math.radians(half_deg),d

def can_hear(epos, ppos, hr, sprinting=False, shooting=False):
    d=math.hypot(ppos[0]-epos[0],ppos[1]-epos[1]); er=hr
    if sprinting: er*=1.5
    if shooting: er*=2.0
    return d<=er
