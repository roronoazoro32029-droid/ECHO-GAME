"""
Finite State Machine — generic FSM used by all enemy types.
Each state is a string key. Transitions are driven by the enemy's
perception and game conditions.
"""


class State:
    """Base class for an FSM state."""

    def __init__(self, name: str):
        self.name = name

    def enter(self, entity):
        """Called once when entering this state."""
        pass

    def update(self, entity, dt, context: dict):
        """Called every frame. Return a state name to transition, or None to stay."""
        return None

    def exit(self, entity):
        """Called once when leaving this state."""
        pass


class StateMachine:
    """Manages a set of named States and drives transitions."""

    def __init__(self):
        self.states: dict[str, State] = {}
        self.current: State | None = None

    def add_state(self, state: State):
        self.states[state.name] = state

    def set_state(self, name: str, entity):
        if self.current:
            self.current.exit(entity)
        self.current = self.states.get(name)
        if self.current:
            self.current.enter(entity)

    def update(self, entity, dt, context: dict):
        if not self.current:
            return
        next_state = self.current.update(entity, dt, context)
        if next_state and next_state != self.current.name:
            self.set_state(next_state, entity)

    @property
    def current_name(self) -> str:
        return self.current.name if self.current else "none"
