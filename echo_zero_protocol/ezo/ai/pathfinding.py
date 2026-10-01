
import heapq
from game.settings import TILE_SIZE, TILE_WALL, TILE_DOOR

def _walkable(tm, r, c, od=None):
    if r<0 or r>=len(tm) or c<0 or c>=len(tm[0]): return False
    t=tm[r][c]
    if t==TILE_WALL: return False
    if t==TILE_DOOR: return od and (r,c) in od
    return True

def find_path(tm, start, goal, od=None, max_iter=600):
    sc,sr=int(start[0]//TILE_SIZE),int(start[1]//TILE_SIZE)
    gc,gr=int(goal[0]//TILE_SIZE),int(goal[1]//TILE_SIZE)
    rows,cols=len(tm),len(tm[0]) if tm else 0
    sr,sc=max(0,min(sr,rows-1)),max(0,min(sc,cols-1))
    gr,gc=max(0,min(gr,rows-1)),max(0,min(gc,cols-1))
    if not _walkable(tm,sr,sc,od) or not _walkable(tm,gr,gc,od): return []
    s=(sr,sc); g=(gr,gc)
    if s==g: return [(gc*TILE_SIZE+TILE_SIZE//2,gr*TILE_SIZE+TILE_SIZE//2)]
    o=[]; heapq.heappush(o,(0,s)); cf={}; gs={s:0}; v=set(); it=0
    nb=[(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    while o and it<max_iter:
        it+=1; _,cur=heapq.heappop(o)
        if cur==g:
            p=[]; n=cur
            while n in cf: p.append((n[1]*TILE_SIZE+TILE_SIZE//2,n[0]*TILE_SIZE+TILE_SIZE//2)); n=cf[n]
            p.reverse(); return p
        if cur in v: continue
        v.add(cur)
        for dr,dc in nb:
            nr,nc=cur[0]+dr,cur[1]+dc
            if not _walkable(tm,nr,nc,od): continue
            if dr!=0 and dc!=0:
                if not _walkable(tm,cur[0]+dr,cur[1],od): continue
                if not _walkable(tm,cur[0],cur[1]+dc,od): continue
            cost=1.414 if(dr!=0 and dc!=0) else 1.0
            tent=gs[cur]+cost; nei=(nr,nc)
            if tent<gs.get(nei,float("inf")):
                cf[nei]=cur; gs[nei]=tent
                heapq.heappush(o,(tent+abs(nei[0]-g[0])+abs(nei[1]-g[1]),nei))
    return []
