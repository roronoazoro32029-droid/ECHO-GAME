
ITEM_DB={
    "medkit":{"name":"Medkit","desc":"Restores 40 HP.","icon_color":(200,40,40),"icon_symbol":"+","stackable":True,"max_stack":5,"usable":True,"category":"consumable"},
    "energy_cell":{"name":"Energy Cell","desc":"Restores 35 Energy.","icon_color":(0,180,220),"icon_symbol":"E","stackable":True,"max_stack":5,"usable":True,"category":"consumable"},
    "ammo_pack":{"name":"Ammo Pack","desc":"Restores 12 rounds.","icon_color":(180,180,80),"icon_symbol":"A","stackable":True,"max_stack":8,"usable":True,"category":"consumable"},
    "emp_charge":{"name":"EMP Charge","desc":"Restores 40 energy.","icon_color":(220,220,60),"icon_symbol":"Q","stackable":True,"max_stack":4,"usable":True,"category":"consumable"},
    "access_card_a":{"name":"Access Card A","desc":"Opens Security Level A doors.","icon_color":(60,200,100),"icon_symbol":"K","stackable":False,"max_stack":1,"usable":False,"category":"key"},
    "data_drive_1":{"name":"Research Log #1","desc":"Fragments of Project ECHO.","icon_color":(160,100,220),"icon_symbol":"D","stackable":False,"max_stack":1,"usable":False,"category":"evidence"},
    "data_drive_2":{"name":"Research Log #2","desc":"Personnel file: Dr. E. Voss.","icon_color":(160,100,220),"icon_symbol":"D","stackable":False,"max_stack":1,"usable":False,"category":"evidence"},
    "fuse":{"name":"Power Fuse","desc":"Restores power to offline systems.","icon_color":(220,160,40),"icon_symbol":"F","stackable":True,"max_stack":3,"usable":False,"category":"component"},
}
class Inventory:
    def __init__(s,max_slots=16): s.items={}; s.max_slots=max_slots
    def add_item(s,iid,count=1):
        if iid not in ITEM_DB: return False
        info=ITEM_DB[iid]
        if iid in s.items: s.items[iid]=min(s.items[iid]+count,info["max_stack"]); return True
        if len(s.items)>=s.max_slots: return False
        s.items[iid]=min(count,info["max_stack"]); return True
    def remove_item(s,iid,count=1):
        if iid not in s.items: return False
        s.items[iid]-=count
        if s.items[iid]<=0: del s.items[iid]
        return True
    def has_item(s,iid): return iid in s.items and s.items[iid]>0
    def get_count(s,iid): return s.items.get(iid,0)
    def get_items_list(s): return list(s.items.items())
    def to_dict(s): return dict(s.items)
    def from_dict(s,d): s.items=dict(d)
    def use_item(s,iid,player):
        if not s.has_item(iid): return None
        info=ITEM_DB.get(iid)
        if not info or not info.get("usable"): return None
        if iid=="medkit":
            if player.health>=player.max_health: return "Health is already full."
            player.health=min(player.max_health,player.health+40); s.remove_item(iid); return "Medkit applied. +40 HP."
        elif iid=="energy_cell":
            if player.energy>=player.max_energy: return "Energy is already full."
            player.energy=min(player.max_energy,player.energy+35); s.remove_item(iid); return "Energy cell used. +35 Energy."
        elif iid=="ammo_pack":
            if player.ammo>=player.max_ammo: return "Ammo is already full."
            player.ammo=min(player.max_ammo,player.ammo+12); s.remove_item(iid); return "Ammo loaded. +12 rounds."
        elif iid=="emp_charge":
            if player.energy>=player.max_energy: return "Energy is already full."
            player.energy=min(player.max_energy,player.energy+40); s.remove_item(iid); return "EMP charge absorbed. +40 Energy."
        return None
