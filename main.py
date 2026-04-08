# main.py

import sys
import pygame
import settings
import helpers
import physics
import rendering
from objects import create_ball


def main():
    pygame.init()

    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    pygame.display.set_caption("Plinko Simulation")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, settings.FONT_SIZE)

    pegs = helpers.generate_pegs()
    partitions = helpers.generate_partitions()

    balls = []
    bin_counts = [0] * settings.BIN_COUNT

    paused = False
    running = True

    step_count = 0
    spawned_balls = 0
    landed_balls = 0

    while running:
        clock.tick(int(1 / settings.DT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused

        if not paused:
            if spawned_balls < settings.TOTAL_BALLS:
                if step_count % settings.SPAWN_INTERVAL_STEPS == 0:
                    for _ in range(settings.BALLS_PER_BATCH):
                        if spawned_balls >= settings.TOTAL_BALLS:
                            break

                        spawn_x, spawn_y = helpers.random_spawn_position()
                        ball = create_ball(spawn_x, spawn_y)
                        balls.append(ball)
                        spawned_balls += 1

            for ball in balls:
                if ball.active:
                    physics.update_ball(ball, pegs, partitions)

                if ball.landed:
                    physics.register_landed_ball(ball, bin_counts)
                    landed_balls += 1

            step_count += 1

        rendering.draw_scene(
            screen,
            font,
            balls,
            pegs,
            partitions,
            bin_counts,
            spawned_balls,
            landed_balls,
            paused
        )

        if spawned_balls == settings.TOTAL_BALLS and landed_balls == settings.TOTAL_BALLS:
            running = False

    pygame.quit()
    helpers.show_distribution(bin_counts)
    sys.exit()


if __name__ == "__main__":
    main()