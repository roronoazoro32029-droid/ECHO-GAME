
import math,random,pygame
from entities.enemy import Enemy
from ai.state_machine import StateMachine,State
from ai.perception import has_line_of_sight,in_field_of_view,can_hear
from game.settings import (HUNTER_SPEED,HUNTER_HEALTH,HUNTER_RADIUS,HUNTER_SIGHT_RANGE,
    HUNTER_SIGHT_ANGLE,HUNTER_DAMAGE,HUNTER_ATTACK_RANGE,HUNTER_FIRE_RATE,HUNTER_HEAR_RANGE,ENEMY_COLORS)

def _see(e,ctx):
    f,d=in_field_of_view(e.pos,e.angle,ctx["player_pos"],HUNTER_SIGHT_ANGLE,HUNTER_SIGHT_RANGE)
    return f and has_line_of_sight(ctx["tile_map"],e.pos,ctx["player_pos"],ctx.get("open_doors"))
def _pd(e,ctx): return math.hypot(ctx["player_pos"][0]-e.pos.x,ctx["player_pos"][1]-e.pos.y)

class HP(State):
    def __init__(s): super().__init__("patrol")
    def enter(s,e): e.patrol_index=getattr(e,"patrol_index",0)
    def update(s,e,dt,ctx):
        if _see(e,ctx): e.last_known_player_pos=tuple(ctx["player_pos"]); return "chase"
        if can_hear(e.pos,ctx["player_pos"],HUNTER_HEAR_RANGE,ctx.get("player_sprinting"),ctx.get("player_shooting")):
            e.last_known_player_pos=tuple(ctx["player_pos"]); return "flank"
        if e.patrol_points:
            e.request_path(ctx["tile_map"],e.patrol_points[e.patrol_index],ctx.get("open_doors"))
            if e.follow_path(dt,ctx["wall_rects"]): e.patrol_index=(e.patrol_index+1)%len(e.patrol_points)
class HC(State):
    def __init__(s): super().__init__("chase")
    def update(s,e,dt,ctx):
        if e.health<e.max_health*0.3: return "retreat"
        if _see(e,ctx):
            e.last_known_player_pos=tuple(ctx["player_pos"])
            if _pd(e,ctx)<=HUNTER_ATTACK_RANGE: return "attack"
            e.request_path(ctx["tile_map"],ctx["player_pos"],ctx.get("open_doors")); e.follow_path(dt,ctx["wall_rects"])
        else: return "flank"
class HF(State):
    def __init__(s): super().__init__("flank"); s.timer=0; s.fo=0
    def enter(s,e): s.timer=5.0; s.fo=random.choice([-1,1])*random.uniform(80,160)
    def update(s,e,dt,ctx):
        s.timer-=dt
        if _see(e,ctx): e.last_known_player_pos=tuple(ctx["player_pos"]); return "chase"
        if e.last_known_player_pos:
            px,py=e.last_known_player_pos; a=math.atan2(py-e.pos.y,px-e.pos.x)
            fx,fy=px+math.cos(a+math.pi/2)*s.fo,py+math.sin(a+math.pi/2)*s.fo
            e.request_path(ctx["tile_map"],(fx,fy),ctx.get("open_doors")); e.follow_path(dt,ctx["wall_rects"])
        if s.timer<=0: return "search"
class HA(State):
    def __init__(s): super().__init__("attack")
    def update(s,e,dt,ctx):
        if e.health<e.max_health*0.3: return "retreat"
        if not _see(e,ctx): return "search"
        if _pd(e,ctx)>HUNTER_ATTACK_RANGE*1.3: return "chase"
        e.face_toward(ctx["player_pos"])
        if e.attack_cooldown<=0:
            e.attack_cooldown=HUNTER_FIRE_RATE
            ctx["enemy_shots"].append({"pos":(e.pos.x,e.pos.y),"angle":e.angle,"damage":HUNTER_DAMAGE,"speed":420,"color":e.color,"enemy":e})
        st=math.sin(pygame.time.get_ticks()/300.0)*80
        sx,sy=e.pos.x+math.cos(e.angle+math.pi/2)*st*dt,e.pos.y+math.sin(e.angle+math.pi/2)*st*dt
        t=pygame.Rect(sx-e.radius,sy-e.radius,e.radius*2,e.radius*2)
        if not any(t.colliderect(w) for w in ctx["wall_rects"]): e.pos.x=sx; e.pos.y=sy
class HS(State):
    def __init__(s): super().__init__("search"); s.timer=0
    def enter(s,e): s.timer=5.0
    def update(s,e,dt,ctx):
        s.timer-=dt
        if _see(e,ctx): e.last_known_player_pos=tuple(ctx["player_pos"]); return "chase"
        if can_hear(e.pos,ctx["player_pos"],HUNTER_HEAR_RANGE,ctx.get("player_sprinting"),ctx.get("player_shooting")):
            e.last_known_player_pos=tuple(ctx["player_pos"]); return "flank"
        if e.last_known_player_pos:
            e.request_path(ctx["tile_map"],e.last_known_player_pos,ctx.get("open_doors"))
            if e.follow_path(dt,ctx["wall_rects"]): e.angle+=2.5*dt
        if s.timer<=0: return "patrol"
class HR(State):
    def __init__(s): super().__init__("retreat"); s.timer=0
    def enter(s,e): s.timer=3.0
    def update(s,e,dt,ctx):
        s.timer-=dt; pp=ctx["player_pos"]; dx,dy=e.pos.x-pp[0],e.pos.y-pp[1]; d=math.hypot(dx,dy)
        if d>0:
            e.request_path(ctx["tile_map"],(e.pos.x+(dx/d)*120,e.pos.y+(dy/d)*120),ctx.get("open_doors"))
            e.follow_path(dt,ctx["wall_rects"])
        if s.timer<=0: return "chase" if e.health>e.max_health*0.3 else "patrol"

class Hunter(Enemy):
    def __init__(s,x,y,patrol_points=None):
        super().__init__(x,y,HUNTER_RADIUS,HUNTER_HEALTH,HUNTER_SPEED,ENEMY_COLORS["hunter"],"hunter")
        s.patrol_points=patrol_points or []; s.patrol_index=0
        s.fsm=StateMachine()
        for st in[HP(),HC(),HF(),HA(),HS(),HR()]: s.fsm.add_state(st)
        s.fsm.set_state("patrol",s)
    def _build_sprite(s):
        sz=s.radius*2+10; s._sprite=pygame.Surface((sz,sz),pygame.SRCALPHA); c=sz//2; r=s.radius
        pts=[(c+r,c),(c-int(r*0.7),c+int(r*0.8)),(c-int(r*0.7),c-int(r*0.8))]
        dim=tuple(max(v//3,0) for v in s.color)
        pygame.draw.polygon(s._sprite,dim,pts); pygame.draw.polygon(s._sprite,s.color,pts,2)
        pygame.draw.circle(s._sprite,s.color,(c+3,c),3)
