
class State:
    def __init__(self, name): self.name = name
    def enter(self, entity): pass
    def update(self, entity, dt, ctx): return None
    def exit(self, entity): pass

class StateMachine:
    def __init__(self): self.states = {}; self.current = None
    def add_state(self, s): self.states[s.name] = s
    def set_state(self, name, entity):
        if self.current: self.current.exit(entity)
        self.current = self.states.get(name)
        if self.current: self.current.enter(entity)
    def update(self, entity, dt, ctx):
        if not self.current: return
        ns = self.current.update(entity, dt, ctx)
        if ns and ns != self.current.name: self.set_state(ns, entity)
    @property
    def current_name(self): return self.current.name if self.current else "none"
