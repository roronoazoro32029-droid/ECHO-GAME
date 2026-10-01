
from data.story_data import CHAPTER_INTROS,RECORDINGS,TERMINAL_DIALOGUES,ENDINGS
class StoryManager:
    def __init__(s):
        s.current_chapter=0;s.terminal_index=0;s.recordings_found=[];s.story_flags={}
        s._tk={0:["ch0_terminal_1","ch0_terminal_2","ch0_terminal_3"],1:["ch1_terminal_1","ch1_terminal_2","ch1_terminal_3"]}
        s._rm={0:{0:"rec_ch0_1",1:"rec_ch0_2"},1:{0:"rec_ch1_1",1:"rec_ch1_2",2:"rec_ch1_3",3:"rec_ch1_4"}}
        s._rc={0:0,1:0}
    def get_terminal_dialogue(s):
        keys=s._tk.get(s.current_chapter,[]);idx=s.terminal_index
        if idx<len(keys): s.terminal_index+=1; return TERMINAL_DIALOGUES.get(keys[idx])
        return None
    def get_terminal_follow_up(s,dlg,cid):
        if not dlg or "choices" not in dlg: return None
        for c in dlg["choices"]:
            if c["id"]==cid: return c.get("follow")
        return None
    def get_next_recording(s):
        ch=s.current_chapter;cnt=s._rc.get(ch,0);recs=s._rm.get(ch,{})
        if cnt in recs:
            rid=recs[cnt];s._rc[ch]=cnt+1
            if rid not in s.recordings_found: s.recordings_found.append(rid)
            return RECORDINGS.get(rid)
        return None
    def get_chapter_intro(s): return CHAPTER_INTROS.get(s.current_chapter)
    def advance_chapter(s):
        n=s.current_chapter+1
        if n<=1: s.current_chapter=n;s.terminal_index=0; return True
        return False
    def is_final_chapter(s): return s.current_chapter>=1
    def determine_ending(s,trust,last_cid=""):
        return "liberation" if last_cid=="trust_echo" or trust>=55 else "containment"
    def get_ending(s,eid): return ENDINGS.get(eid)
    def to_dict(s): return {"chapter":s.current_chapter,"terminal_index":s.terminal_index,"recordings_found":s.recordings_found,"story_flags":dict(s.story_flags),"recording_counters":dict(s._rc)}
    def from_dict(s,d):
        s.current_chapter=d.get("chapter",0);s.terminal_index=d.get("terminal_index",0)
        s.recordings_found=d.get("recordings_found",[]);s.story_flags=d.get("story_flags",{})
        s._rc={int(k):v for k,v in d.get("recording_counters",{}).items()}
