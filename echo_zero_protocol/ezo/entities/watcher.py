
import math,random,pygame
from entities.enemy import Enemy
from ai.state_machine import StateMachine,State
from ai.perception import has_line_of_sight,in_field_of_view
from game.settings import (WATCHER_SPEED,WATCHER_HEALTH,WATCHER_RADIUS,WATCHER_SIGHT_RANGE,WATCHER_SIGHT_ANGLE,ENEMY_COLORS)

def _see(e,ctx):
    f,d=in_field_of_view(e.pos,e.angle,ctx["player_pos"],WATCHER_SIGHT_ANGLE,WATCHER_SIGHT_RANGE)
    return f and has_line_of_sight(ctx["tile_map"],e.pos,ctx["player_pos"],ctx.get("open_doors"))

class Patrol(State):
    def __init__(s): super().__init__("patrol")
    def enter(s,e): e.patrol_index=getattr(e,"patrol_index",0)
    def update(s,e,dt,ctx):
        if _see(e,ctx): e.last_known_player_pos=ctx["player_pos"]; e.alert_level=100; return "alert"
        if e.patrol_points:
            if e.move_toward(e.patrol_points[e.patrol_index],dt,ctx["wall_rects"]):
                e.patrol_index=(e.patrol_index+1)%len(e.patrol_points)
class Scan(State):
    def __init__(s): super().__init__("scan"); s.timer=0
    def enter(s,e): s.timer=2.0
    def update(s,e,dt,ctx):
        s.timer-=dt; e.angle+=1.5*dt
        if _see(e,ctx): e.last_known_player_pos=ctx["player_pos"]; return "alert"
        if s.timer<=0: return "patrol"
class Alert(State):
    def __init__(s): super().__init__("alert"); s.timer=0
    def enter(s,e): s.timer=4.0
    def update(s,e,dt,ctx):
        s.timer-=dt; pp=ctx["player_pos"]
        if _see(e,ctx):
            e.last_known_player_pos=pp; e.face_toward(pp); s.timer=4.0
            dx,dy=e.pos.x-pp[0],e.pos.y-pp[1]; d=math.hypot(dx,dy)
            if d<150 and d>0: e.move_toward((e.pos.x+(dx/d)*60,e.pos.y+(dy/d)*60),dt,ctx["wall_rects"])
        else: e.alert_level=max(0,e.alert_level-20*dt)
        if s.timer<=0 or e.alert_level<=0: return "scan"

class Watcher(Enemy):
    def __init__(s,x,y,patrol_points=None):
        super().__init__(x,y,WATCHER_RADIUS,WATCHER_HEALTH,WATCHER_SPEED,ENEMY_COLORS["watcher"],"watcher")
        s.patrol_points=patrol_points or []; s.patrol_index=0
        s.fsm=StateMachine(); s.fsm.add_state(Patrol()); s.fsm.add_state(Scan()); s.fsm.add_state(Alert()); s.fsm.set_state("patrol",s)
    def _build_sprite(s):
        sz=s.radius*2+10; s._sprite=pygame.Surface((sz,sz),pygame.SRCALPHA); c=sz//2; r=s.radius
        pts=[(c+r,c),(c,c+r),(c-r,c),(c,c-r)]; dim=tuple(max(v//3,0) for v in s.color)
        pygame.draw.polygon(s._sprite,dim,pts); pygame.draw.polygon(s._sprite,s.color,pts,2)
        pygame.draw.circle(s._sprite,s.color,(c+4,c),2)
