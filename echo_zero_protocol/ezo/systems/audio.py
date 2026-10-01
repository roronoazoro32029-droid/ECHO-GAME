"""Audio System — procedural music and SFX. All synthesized from waveforms."""
import math,array,random,pygame
SAMPLE_RATE=22050; BITS=16; MAX_AMP=2**(BITS-1)-1

class AudioManager:
    def __init__(self):
        self.enabled=False; self.sfx={}; self.music_tracks={}
        self.current_music=None; self.music_channel=None
        self.combat_active=False; self._combat_cd=0.0
        try:
            pygame.mixer.init(SAMPLE_RATE,-BITS,1,1024)
            pygame.mixer.set_num_channels(16)
            self.music_channel=pygame.mixer.Channel(0); self.enabled=True
        except Exception as e:
            print(f"Audio init failed (silent mode): {e}"); return
        self._gen_sfx(); self._gen_music()

    @staticmethod
    def _snd(samples):
        buf=array.array("h")
        for s in samples: buf.append(int(max(-1,min(1,s))*MAX_AMP))
        return pygame.mixer.Sound(buffer=buf)
    @staticmethod
    def _sine(f,d,v=0.5): n=int(SAMPLE_RATE*d); return[v*math.sin(2*math.pi*f*i/SAMPLE_RATE)for i in range(n)]
    @staticmethod
    def _sq(f,d,v=0.3): n=int(SAMPLE_RATE*d);p=SAMPLE_RATE/f if f>0 else SAMPLE_RATE; return[v*(1.0 if(i%int(p))<p/2 else-1.0)for i in range(n)]
    @staticmethod
    def _noise(d,v=0.3): return[v*random.uniform(-1,1)for _ in range(int(SAMPLE_RATE*d))]
    @staticmethod
    def _env(s,a=0.01,r=0.05,sus=1.0):
        n=len(s);an=int(SAMPLE_RATE*a);rn=int(SAMPLE_RATE*r)
        return[s[i]*(i/max(an,1) if i<an else(n-i)/max(rn,1) if i>n-rn else sus)for i in range(n)]
    @staticmethod
    def _mix(*t):
        ml=max(len(x)for x in t);r=[0.0]*ml
        for tr in t:
            for i in range(len(tr)):r[i]+=tr[i]
        pk=max(abs(x)for x in r)if r else 1.0
        return[x/pk for x in r]if pk>1 else r
    @staticmethod
    def _lp(s,c=0.1):
        o=[0.0]*len(s);o[0]=s[0]
        for i in range(1,len(s)):o[i]=o[i-1]+c*(s[i]-o[i-1])
        return o
    @staticmethod
    def _delay(s,d=0.15,fb=0.4):
        dn=int(SAMPLE_RATE*d);o=list(s)
        for i in range(dn,len(o)):o[i]+=o[i-dn]*fb
        pk=max(abs(x)for x in o)if o else 1.0
        return[x/pk for x in o]if pk>1 else o

    def _gen_sfx(self):
        # Gunshots
        self.sfx["shoot_pistol"]=self._snd(self._env(self._mix(self._noise(0.08,0.6),self._sine(280,0.08,0.3)),a=0.001,r=0.04))
        zap=self._sine(150,0.15,0.4);buzz=self._sq(90,0.15,0.2)
        self.sfx["shoot_rifle"]=self._snd(self._env(self._mix(zap,buzz,self._noise(0.1,0.3)),a=0.005,r=0.08))
        self.sfx["enemy_shoot"]=self._snd(self._env(self._mix(self._sine(400,0.06,0.3),self._noise(0.04,0.2)),a=0.001,r=0.03))
        # Impact/death
        self.sfx["impact"]=self._snd(self._env(self._mix(self._sine(100,0.1,0.4),self._noise(0.03,0.3)),r=0.06))
        desc=[0.5*math.sin(2*math.pi*(600-i*2)*i/SAMPLE_RATE)for i in range(int(SAMPLE_RATE*0.4))]
        self.sfx["enemy_death"]=self._snd(self._env(self._mix(desc,self._noise(0.3,0.3)),r=0.15))
        # EMP
        sweep=[0.4*math.sin(2*math.pi*(50+i*0.8)*i/SAMPLE_RATE)for i in range(int(SAMPLE_RATE*0.5))]
        self.sfx["emp"]=self._snd(self._env(self._mix(sweep,self._lp(self._noise(0.5,0.3),0.05)),a=0.01,r=0.2))
        # Door
        sl=[0.3*math.sin(2*math.pi*(80+i*0.3)*i/SAMPLE_RATE)for i in range(int(SAMPLE_RATE*0.4))]
        self.sfx["door_open"]=self._snd(self._env(self._mix(sl,self._lp(self._noise(0.3,0.2),0.08)),a=0.02,r=0.15))
        # Pickup/terminal/heal/recording
        self.sfx["pickup"]=self._snd(self._env(self._sine(800,0.05,0.3)+self._sine(1200,0.05,0.2),a=0.005,r=0.03))
        self.sfx["terminal"]=self._snd(self._env(self._sine(600,0.08,0.25)+self._sine(900,0.08,0.25)+self._sine(1100,0.12,0.2),a=0.005,r=0.05))
        hs=[0.3*math.sin(2*math.pi*(400+i*0.5)*i/SAMPLE_RATE)for i in range(int(SAMPLE_RATE*0.5))]
        self.sfx["heal"]=self._snd(self._env(hs,a=0.05,r=0.2))
        self.sfx["ui_nav"]=self._snd(self._env(self._sine(1000,0.03,0.15),r=0.01))
        self.sfx["ui_select"]=self._snd(self._env(self._sine(800,0.04,0.2)+self._sine(1200,0.06,0.2),r=0.02))
        self.sfx["player_hurt"]=self._snd(self._env(self._mix(self._sine(100,0.15,0.4),self._noise(0.1,0.3)),a=0.005,r=0.1))
        r1=self._sine(500,0.1,0.2);r2=self._sine(700,0.1,0.2);r3=self._sine(600,0.15,0.2)
        self.sfx["recording"]=self._snd(self._env(r1+r2+r3,a=0.01,r=0.08))
        su=[0.3*math.sin(2*math.pi*(200+i*0.2)*i/SAMPLE_RATE)for i in range(int(SAMPLE_RATE*1.5))]
        self.sfx["chapter_transition"]=self._snd(self._delay(self._env(self._mix(su,self._lp(self._sine(150,1.5,0.2),0.02)),a=0.3,r=0.5),0.2,0.3))

    def _gen_music(self):
        self.music_tracks["menu"]=self._snd(self._gen_menu())
        self.music_tracks["explore"]=self._snd(self._gen_explore())
        self.music_tracks["combat"]=self._snd(self._gen_combat())

    def _gen_menu(self):
        d=12.0;n=int(SAMPLE_RATE*d)
        drone=[0.15*math.sin(2*math.pi*55*i/SAMPLE_RATE+0.5*math.sin(2*math.pi*0.2*i/SAMPLE_RATE))for i in range(n)]
        pc=[0.08*math.sin(2*math.pi*130.8*i/SAMPLE_RATE)for i in range(n)]
        pe=[0.06*math.sin(2*math.pi*155.6*i/SAMPLE_RATE)for i in range(n)]
        pg=[0.06*math.sin(2*math.pi*196.0*i/SAMPLE_RATE)for i in range(n)]
        sh=[0.03*math.sin(2*math.pi*1760*i/SAMPLE_RATE)*(0.5+0.5*math.sin(2*math.pi*0.1*i/SAMPLE_RATE))for i in range(n)]
        return self._lp(self._env(self._mix(drone,pc,pe,pg,sh),a=2.0,r=2.0),0.04)

    def _gen_explore(self):
        d=16.0;n=int(SAMPLE_RATE*d)
        drone=[0.12*math.sin(2*math.pi*48*i/SAMPLE_RATE+0.8*math.sin(2*math.pi*0.15*i/SAMPLE_RATE))for i in range(n)]
        t1=[0.05*math.sin(2*math.pi*146.8*i/SAMPLE_RATE)*(0.5+0.5*math.sin(2*math.pi*0.25*i/SAMPLE_RATE))for i in range(n)]
        t2=[0.04*math.sin(2*math.pi*207.7*i/SAMPLE_RATE)*(0.5+0.5*math.sin(2*math.pi*0.18*i/SAMPLE_RATE))for i in range(n)]
        pulse=[0.0]*n; bi=int(SAMPLE_RATE*1.2)
        for s in range(0,n,bi):
            for j in range(min(int(SAMPLE_RATE*0.08),n-s)):
                pulse[s+j]=0.15*math.sin(2*math.pi*40*j/SAMPLE_RATE)*(1-j/(SAMPLE_RATE*0.08))
        return self._lp(self._env(self._mix(drone,t1,t2,pulse),a=1.5,r=1.5),0.05)

    def _gen_combat(self):
        d=8.0;n=int(SAMPLE_RATE*d)
        bass=[0.2*math.sin(2*math.pi*55*i/SAMPLE_RATE)for i in range(n)]
        pi_=int(SAMPLE_RATE*0.214);pulse=[0.0]*n
        for s in range(0,n,pi_):
            for j in range(min(int(SAMPLE_RATE*0.05),n-s)):
                pulse[s+j]=0.12*math.sin(2*math.pi*80*j/SAMPLE_RATE)*(1-j/(SAMPLE_RATE*0.05))
        si=int(SAMPLE_RATE*0.857);stab=[0.0]*n
        for s in range(0,n,si):
            for j in range(min(int(SAMPLE_RATE*0.1),n-s)):
                stab[s+j]=0.08*(math.sin(2*math.pi*311*j/SAMPLE_RATE)+math.sin(2*math.pi*466*j/SAMPLE_RATE))*(1-j/(SAMPLE_RATE*0.1))
        hi=int(SAMPLE_RATE*0.107);hh=[0.0]*n
        for s in range(0,n,hi):
            for j in range(min(int(SAMPLE_RATE*0.02),n-s)):
                hh[s+j]=0.04*random.uniform(-1,1)*(1-j/(SAMPLE_RATE*0.02))
        return self._lp(self._env(self._mix(bass,pulse,stab,hh),a=0.5,r=0.5),0.08)

    def play_sfx(self,name,volume=0.5):
        if not self.enabled: return
        s=self.sfx.get(name)
        if s: s.set_volume(max(0,min(1,volume))); s.play()
    def play_music(self,track,volume=0.3,fade_ms=1000):
        if not self.enabled or self.current_music==track: return
        t=self.music_tracks.get(track)
        if not t: return
        self.current_music=track; t.set_volume(max(0,min(1,volume)))
        if self.music_channel: self.music_channel.fadeout(fade_ms); self.music_channel.play(t,loops=-1,fade_ms=fade_ms)
    def stop_music(self,fade_ms=1000):
        if not self.enabled: return
        if self.music_channel: self.music_channel.fadeout(fade_ms)
        self.current_music=None
    def update(self,dt,alert=False):
        if not self.enabled: return
        if alert:
            self._combat_cd=5.0
            if not self.combat_active: self.combat_active=True; self.play_music("combat",0.35,800)
        else:
            self._combat_cd=max(0,self._combat_cd-dt)
            if self._combat_cd<=0 and self.combat_active: self.combat_active=False; self.play_music("explore",0.25,1500)
