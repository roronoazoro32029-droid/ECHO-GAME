
class PlayerBehavior:
    def __init__(self):
        self.aggression=0.0; self.stealth=0.0; self.exploration=0.0
        self.risk_taking=0.0; self.resource_usage=0.0
        self._kills=0; self._shots_fired=0; self._damage_dealt=0
        self._enemies_avoided=0; self._time_unseen=0.0
        self._rooms_visited=set(); self._terminals_accessed=0
        self._evidence_found=0; self._low_health_time=0.0
        self._items_used=0; self._doors_opened=0; self._total_play_time=0.0
    def on_kill(self): self._kills+=1; self._recalc()
    def on_shot_fired(self): self._shots_fired+=1; self._recalc()
    def on_damage_dealt(self,a): self._damage_dealt+=a; self._recalc()
    def on_enemy_avoided(self): self._enemies_avoided+=1; self._recalc()
    def on_terminal_accessed(self): self._terminals_accessed+=1; self._recalc()
    def on_evidence_found(self): self._evidence_found+=1; self._recalc()
    def on_low_health(self,dt): self._low_health_time+=dt; self._recalc()
    def on_item_used(self): self._items_used+=1; self._recalc()
    def on_door_opened(self): self._doors_opened+=1; self._recalc()
    def on_room_visited(self,rid): self._rooms_visited.add(rid); self._recalc()
    def update(self,dt,hp,mhp):
        self._total_play_time+=dt
        if hp<mhp*0.35: self.on_low_health(dt)
    def _recalc(self):
        self.aggression=min(100,self._kills*15+self._shots_fired*1.5+self._damage_dealt*0.1)
        self.stealth=max(0,min(100,self._enemies_avoided*20+self._time_unseen*0.3-self.aggression*0.3))
        self.exploration=min(100,len(self._rooms_visited)*12+self._terminals_accessed*15+self._evidence_found*20+self._doors_opened*5)
        self.risk_taking=min(100,self._low_health_time*2+self.aggression*0.3)
        self.resource_usage=min(100,self._items_used*12)
    def get_profile(self):
        s={"aggressive":self.aggression,"stealthy":self.stealth,"explorer":self.exploration,"reckless":self.risk_taking}
        if max(s.values())<15: return "balanced"
        return max(s,key=s.get)
    def to_dict(self):
        return {"aggression":round(self.aggression,1),"stealth":round(self.stealth,1),"exploration":round(self.exploration,1),
                "risk_taking":round(self.risk_taking,1),"resource_usage":round(self.resource_usage,1),
                "kills":self._kills,"shots_fired":self._shots_fired,"terminals_accessed":self._terminals_accessed,
                "evidence_found":self._evidence_found,"rooms_visited":list(self._rooms_visited),
                "items_used":self._items_used,"play_time":round(self._total_play_time,1)}
    def from_dict(self,d):
        self.aggression=d.get("aggression",0);self.stealth=d.get("stealth",0)
        self.exploration=d.get("exploration",0);self.risk_taking=d.get("risk_taking",0)
        self.resource_usage=d.get("resource_usage",0);self._kills=d.get("kills",0)
        self._shots_fired=d.get("shots_fired",0);self._terminals_accessed=d.get("terminals_accessed",0)
        self._evidence_found=d.get("evidence_found",0);self._rooms_visited=set(d.get("rooms_visited",[]))
        self._items_used=d.get("items_used",0);self._total_play_time=d.get("play_time",0)
