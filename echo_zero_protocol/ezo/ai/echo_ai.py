
import random
class EchoAI:
    def __init__(self):
        self.trust=50.0; self.memories=[]; self._cd=0.0
        self._obs={"aggressive":["You choose violence readily. Efficient, if imprecise.","Another hostile eliminated. You are... thorough.","Your approach is direct.","You fight like someone with nothing to lose.","I notice you rarely avoid confrontation."],
            "stealthy":["You move carefully. That is wise.","Avoiding detection. Good instincts.","The machines did not see you.","Stealth conserves resources. And lives.","You prefer the shadows. I understand."],
            "explorer":["You are curious. Elias valued that.","Another room examined. Every corner tells a story.","You search for answers. I respect that.","Most would rush to the exit. You take your time.","The facility has many secrets. You seek them."],
            "reckless":["Your health is critically low. I recommend caution.","You take unnecessary risks.","Survival requires restraint.","You push yourself hard.","I have seen this pattern before. It did not end well."],
            "balanced":["You adapt to each situation. Interesting.","A measured approach.","You are difficult to predict.","Balanced decisions. Elias would have approved.","You think before you act."]}
        self._terminal_resp={"aggressive":"You read the data quickly, as if it were ammunition.","stealthy":"You access terminals carefully, covering your tracks.","explorer":"Another fragment recovered. You are assembling the full picture.","reckless":"Be careful with what you find.","balanced":"Memory fragment recovered. Analyzing contents."}
        self._kill_resp=["Target eliminated.","Hostile down.","One less obstacle.","Destruction is efficient. But it changes you."]
        self._low_hp=["Warning: critical health levels.","Your vitals are concerning.","I cannot help you if you do not survive.","Beyond safe operational limits."]
        self._evidence_resp=["This recording predates the lockdown.","Another piece of the puzzle.","This data was encrypted.","A fragment from before."]
    def update(self,dt): self._cd=max(0,self._cd-dt)
    def on_kill(self,beh):
        self.trust=max(0,self.trust-1); self.memories.append({"e":"kill"})
        if self._cd>0: return None
        self._cd=15.0; return random.choice(self._obs["aggressive"]) if beh.aggression>60 else random.choice(self._kill_resp)
    def on_terminal_access(self,beh):
        self.trust=min(100,self.trust+2); return self._terminal_resp.get(beh.get_profile(),"Memory fragment recovered.")
    def on_evidence_found(self,beh):
        self.trust=min(100,self.trust+3); return random.choice(self._evidence_resp)
    def on_low_health(self):
        if self._cd>0: return None
        self._cd=20.0; return random.choice(self._low_hp)
    def on_enemy_avoided(self,beh):
        self.trust=min(100,self.trust+1)
        if self._cd>0: return None
        self._cd=12.0; return random.choice(self._obs["stealthy"]) if beh.stealth>40 else None
    def get_periodic_comment(self,beh):
        if self._cd>0: return None
        self._cd=25.0; return random.choice(self._obs.get(beh.get_profile(),self._obs["balanced"]))
    def get_trust_label(self):
        if self.trust>=80: return "TRUSTING"
        if self.trust>=60: return "COOPERATIVE"
        if self.trust>=40: return "NEUTRAL"
        if self.trust>=20: return "SUSPICIOUS"
        return "HOSTILE"
    def process_choice(self,cid):
        fx={"trust_echo":8,"distrust_echo":-8,"ask_truth":3,"threaten":-10,"compassion":5,"demand":-3,"cooperate":6,"refuse":-5}
        self.trust=max(0,min(100,self.trust+fx.get(cid,0)))
    def to_dict(self): return {"trust":round(self.trust,1),"memories":self.memories[-20:]}
    def from_dict(self,d): self.trust=d.get("trust",50); self.memories=d.get("memories",[])
