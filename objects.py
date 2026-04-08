# objects.py

import random
import settings


class Ball:
    def __init__(self, x, y, vx, vy):
        # Position
        self.x = float(x)
        self.y = float(y)

        # Velocity
        self.vx = float(vx)
        self.vy = float(vy)

        # Physical properties
        self.radius = settings.BALL_RADIUS
        self.mass = settings.BALL_MASS

        # State flags
        self.active = True
        self.landed = False


# Create a ball with random initial velocity
def create_ball(x, y):
    vx = random.uniform(settings.INITIAL_VX_MIN, settings.INITIAL_VX_MAX)
    vy = random.uniform(settings.INITIAL_VY_MIN, settings.INITIAL_VY_MAX)
    return Ball(x, y, vx, vy)