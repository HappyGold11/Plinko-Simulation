# physics.py

import math
from scipy.integrate import ode

import settings
import helpers


# Derivative function
def derivative(t, state):
    x, y, vx, vy = state

    ax = 0.0
    ay = -settings.GRAVITY

    return [vx, vy, ax, ay]


# Integrate one ball forward by dt
def integrate_ball(ball, dt):
    solver = ode(derivative).set_integrator("dop853")
    solver.set_initial_value([ball.x, ball.y, ball.vx, ball.vy], 0.0)
    solver.integrate(dt)

    ball.x, ball.y, ball.vx, ball.vy = solver.y


# Update one ball
def update_ball(ball, pegs, partitions):
    if not ball.active:
        return

    sub_dt = settings.DT / settings.PHYSICS_SUBSTEPS

    for _ in range(settings.PHYSICS_SUBSTEPS):
        if not ball.active:
            break

        integrate_ball(ball, sub_dt)

        # Damping
        ball.vx *= settings.LINEAR_DAMPING
        ball.vy *= settings.LINEAR_DAMPING

        # Land immediately once floor is reached
        if check_bin_landing(ball):
            break

        # Collisions
        handle_wall_collisions(ball)
        handle_partition_collisions(ball, partitions)
        handle_peg_collisions(ball, pegs)

        # Check again after collision response
        if check_bin_landing(ball):
            break


# Collision with board walls
def handle_wall_collisions(ball):
    if ball.y <= ball.radius:
        return

    wall_segments = helpers.get_wall_segments()

    for x1, y1, x2, y2 in wall_segments:
        cx, cy = helpers.closest_point_on_segment(ball.x, ball.y, x1, y1, x2, y2)

        dx = ball.x - cx
        dy = ball.y - cy
        dist = math.sqrt(dx * dx + dy * dy)

        min_dist = ball.radius + settings.COLLISION_EPSILON

        if dist == 0:
            continue

        if dist < min_dist:
            nx = dx / dist
            ny = dy / dist

            overlap = min_dist - dist
            ball.x += nx * overlap
            ball.y += ny * overlap

            vn = ball.vx * nx + ball.vy * ny

            if vn < 0:
                ball.vx -= (1 + settings.RESTITUTION_WALL) * vn * nx
                ball.vy -= (1 + settings.RESTITUTION_WALL) * vn * ny


# Collision with bin partitions
def handle_partition_collisions(ball, partitions):
    if ball.y > settings.PARTITION_HEIGHT:
        return
    
    min_dist = ball.radius + (settings.PARTITION_THICKNESS / 2) + settings.COLLISION_EPSILON

    for px in partitions:
        dx = ball.x - px

        if abs(dx) < min_dist:
            if dx < 0:
                ball.x = px - min_dist
            else:
                ball.x = px + min_dist

            ball.vx = -ball.vx * settings.RESTITUTION_PARTITION


# Collision with pegs
def handle_peg_collisions(ball, pegs):
    min_dist = ball.radius + settings.PEG_RADIUS + settings.COLLISION_EPSILON

    for px, py in pegs:
        dx = ball.x - px
        dy = ball.y - py
        dist = math.sqrt(dx * dx + dy * dy)

        if dist == 0:
            continue

        if dist < min_dist:
            nx = dx / dist
            ny = dy / dist

            overlap = min_dist - dist
            ball.x += nx * overlap
            ball.y += ny * overlap

            vn = ball.vx * nx + ball.vy * ny

            if vn < 0:
                ball.vx -= (1 + settings.RESTITUTION_PEG) * vn * nx
                ball.vy -= (1 + settings.RESTITUTION_PEG) * vn * ny


# Check if ball has landed
def check_bin_landing(ball):
    if ball.y <= ball.radius:
        ball.y = 0.0
        ball.active = False
        ball.landed = True
        return True

    return False


# Count landed ball
def register_landed_ball(ball, bin_counts):
    if not ball.landed:
        return

    idx = helpers.get_bin_index(ball.x)
    bin_counts[idx] += 1
    ball.landed = False