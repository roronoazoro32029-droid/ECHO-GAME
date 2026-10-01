import random, pygame
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, CAMERA_SMOOTHING, CAMERA_SHAKE_DECAY

class Camera:
    def __init__(self):
        self.offset = pygame.math.Vector2(0, 0)
        self.target = pygame.math.Vector2(0, 0)
        self.shake_amount = 0.0
        self.shake_offset = pygame.math.Vector2(0, 0)
    def update(self, target_pos, dt):
        self.target.x = target_pos[0] - SCREEN_WIDTH / 2
        self.target.y = target_pos[1] - SCREEN_HEIGHT / 2
        self.offset.x += (self.target.x - self.offset.x) * CAMERA_SMOOTHING
        self.offset.y += (self.target.y - self.offset.y) * CAMERA_SMOOTHING
        if self.shake_amount > 0.5:
            self.shake_offset.x = random.uniform(-self.shake_amount, self.shake_amount)
            self.shake_offset.y = random.uniform(-self.shake_amount, self.shake_amount)
            self.shake_amount *= CAMERA_SHAKE_DECAY
        else:
            self.shake_amount = 0; self.shake_offset.x = 0; self.shake_offset.y = 0
    def apply(self, world_pos):
        return (world_pos[0]-self.offset.x+self.shake_offset.x, world_pos[1]-self.offset.y+self.shake_offset.y)
    def apply_rect(self, rect):
        return pygame.Rect(rect.x-self.offset.x+self.shake_offset.x, rect.y-self.offset.y+self.shake_offset.y, rect.w, rect.h)
    def shake(self, intensity=8):
        self.shake_amount = intensity
