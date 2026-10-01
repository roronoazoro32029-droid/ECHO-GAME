
import math,random,pygame
from entities.enemy import Enemy
from ai.state_machine import StateMachine,State
from ai.perception import has_line_of_sight,in_field_of_view,can_hear
from game.settings import (SENTINEL_SPEED,SENTINEL_HEALTH,SENTINEL_RADIUS,SENTINEL_SIGHT_RANGE,
    SENTINEL_SIGHT_ANGLE,SENTINEL_DAMAGE,SENTINEL_ATTACK_RANGE,SENTINEL_FIRE_RATE,ENEMY_COLORS)

def _see(e,ctx):
    f,d=in_field_of_view(e.pos,e.angle,ctx["player_pos"],SENTINEL_SIGHT_ANGLE,SENTINEL_SIGHT_RANGE)
    return f and has_line_of_sight(ctx["tile_map"],e.pos,ctx["player_pos"],ctx.get("open_doors"))
def _pd(e,ctx): return math.hypot(ctx["player_pos"][0]-e.pos.x,ctx["player_pos"][1]-e.pos.y)

class SPatrol(State):
    def __init__(s): super().__init__("patrol")
    def enter(s,e): e.patrol_index=getattr(e,"patrol_index",0)
    def update(s,e,dt,ctx):
        if _see(e,ctx): e.last_known_player_pos=tuple(ctx["player_pos"]); return "chase"
        if can_hear(e.pos,ctx["player_pos"],180,ctx.get("player_sprinting"),ctx.get("player_shooting")):
            e.last_known_player_pos=tuple(ctx["player_pos"]); return "investigate"
        if e.patrol_points:
            e.request_path(ctx["tile_map"],e.patrol_points[e.patrol_index],ctx.get("open_doors"))
            if e.follow_path(dt,ctx["wall_rects"]): e.patrol_index=(e.patrol_index+1)%len(e.patrol_points)
        else: e.angle+=0.5*dt
class SInvestigate(State):
    def __init__(s): super().__init__("investigate"); s.timer=0
    def enter(s,e): s.timer=5.0
    def update(s,e,dt,ctx):
        s.timer-=dt
        if _see(e,ctx): e.last_known_player_pos=tuple(ctx["player_pos"]); return "chase"
        if e.last_known_player_pos:
            e.request_path(ctx["tile_map"],e.last_known_player_pos,ctx.get("open_doors"))
            if e.follow_path(dt,ctx["wall_rects"]): return "search"
        if s.timer<=0: return "patrol"
class SChase(State):
    def __init__(s): super().__init__("chase")
    def update(s,e,dt,ctx):
        if _see(e,ctx):
            e.last_known_player_pos=tuple(ctx["player_pos"])
            if _pd(e,ctx)<=SENTINEL_ATTACK_RANGE: return "attack"
            e.request_path(ctx["tile_map"],ctx["player_pos"],ctx.get("open_doors")); e.follow_path(dt,ctx["wall_rects"])
        else: return "search"
class SAttack(State):
    def __init__(s): super().__init__("attack")
    def update(s,e,dt,ctx):
        if not _see(e,ctx): return "search"
        if _pd(e,ctx)>SENTINEL_ATTACK_RANGE*1.2: return "chase"
        e.face_toward(ctx["player_pos"])
        if e.attack_cooldown<=0:
            e.attack_cooldown=SENTINEL_FIRE_RATE
            ctx["enemy_shots"].append({"pos":(e.pos.x,e.pos.y),"angle":e.angle,"damage":SENTINEL_DAMAGE,"speed":350,"color":e.color,"enemy":e})
        st=math.sin(pygame.time.get_ticks()/500.0)*40
        sx,sy=e.pos.x+math.cos(e.angle+math.pi/2)*st*dt,e.pos.y+math.sin(e.angle+math.pi/2)*st*dt
        t=pygame.Rect(sx-e.radius,sy-e.radius,e.radius*2,e.radius*2)
        if not any(t.colliderect(w) for w in ctx["wall_rects"]): e.pos.x=sx; e.pos.y=sy
class SSearch(State):
    def __init__(s): super().__init__("search"); s.timer=0; s.sd=1
    def enter(s,e): s.timer=6.0; s.sd=random.choice([-1,1])
    def update(s,e,dt,ctx):
        s.timer-=dt
        if _see(e,ctx): e.last_known_player_pos=tuple(ctx["player_pos"]); return "chase"
        if e.last_known_player_pos:
            d=math.hypot(e.pos.x-e.last_known_player_pos[0],e.pos.y-e.last_known_player_pos[1])
            if d>30: e.request_path(ctx["tile_map"],e.last_known_player_pos,ctx.get("open_doors")); e.follow_path(dt,ctx["wall_rects"])
            else: e.angle+=s.sd*2.0*dt
        if s.timer<=0: return "patrol"

class Sentinel(Enemy):
    def __init__(s,x,y,patrol_points=None):
        super().__init__(x,y,SENTINEL_RADIUS,SENTINEL_HEALTH,SENTINEL_SPEED,ENEMY_COLORS["sentinel"],"sentinel")
        s.patrol_points=patrol_points or []; s.patrol_index=0
        s.fsm=StateMachine()
        for st in[SPatrol(),SInvestigate(),SChase(),SAttack(),SSearch()]: s.fsm.add_state(st)
        s.fsm.set_state("patrol",s)
    def _build_sprite(s):
        sz=s.radius*2+10; s._sprite=pygame.Surface((sz,sz),pygame.SRCALPHA); c=sz//2; r=s.radius
        pts=[(c+int(r*math.cos(math.radians(60*i-30))),c+int(r*math.sin(math.radians(60*i-30)))) for i in range(6)]
        dim=tuple(max(v//3,0) for v in s.color)
        pygame.draw.polygon(s._sprite,dim,pts); pygame.draw.polygon(s._sprite,s.color,pts,2)
        pygame.draw.circle(s._sprite,s.color,(c+5,c),3)
