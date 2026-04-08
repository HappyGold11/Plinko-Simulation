# rendering.py

import pygame
import settings
import helpers
import pygame.gfxdraw


# Draw the full simulation frame
def draw_scene(screen, font, balls, pegs, partitions, bin_counts, spawned_balls, landed_balls, paused):
    screen.fill(settings.BACKGROUND_COLOR)

    draw_bins(screen, partitions, bin_counts)
    draw_walls(screen)
    draw_pegs(screen, pegs)
    draw_balls(screen, balls)
    draw_hud(screen, font, spawned_balls, landed_balls, paused)

    pygame.display.flip()


# Draw all balls
def draw_balls(screen, balls):
    radius_px = helpers.to_pixels(settings.BALL_RADIUS)

    for ball in balls:
        if not ball.active:
            continue

        x, y = helpers.to_screen(ball.x, ball.y)
        pygame.gfxdraw.filled_circle(screen, x, y, radius_px, settings.BALL_COLOR)
        pygame.gfxdraw.aacircle(screen, x, y, radius_px, settings.BALL_COLOR)


# Draw all pegs
def draw_pegs(screen, pegs):
    radius_px = helpers.to_pixels(settings.PEG_RADIUS)

    for peg_x, peg_y in pegs:
        x, y = helpers.to_screen(peg_x, peg_y)
        pygame.gfxdraw.filled_circle(screen, x, y, radius_px, settings.PEG_COLOR)
        pygame.gfxdraw.aacircle(screen, x, y, radius_px, settings.PEG_COLOR)


# Draw board walls
def draw_walls(screen):
    wall_segments = helpers.get_wall_segments()
    wall_width = max(1, helpers.to_pixels(settings.WALL_THICKNESS))

    for x1, y1, x2, y2 in wall_segments:
        sx1, sy1 = helpers.to_screen(x1, y1)
        sx2, sy2 = helpers.to_screen(x2, y2)
        pygame.draw.line(screen, settings.WALL_COLOR, (sx1, sy1), (sx2, sy2), wall_width)


# Draw bins and counters
def draw_bins(screen, partitions, bin_counts):
    left_x, right_x = helpers.get_board_bounds()

    floor_y = helpers.to_screen(0, 0)[1]
    top_y = helpers.to_screen(0, settings.PARTITION_HEIGHT)[1]

    left_screen_x = helpers.to_screen(left_x, 0)[0]
    right_screen_x = helpers.to_screen(right_x, 0)[0]

    wall_width = max(1, helpers.to_pixels(settings.WALL_THICKNESS))
    partition_width = max(1, helpers.to_pixels(settings.PARTITION_THICKNESS))

    pygame.draw.line(
        screen,
        settings.WALL_COLOR,
        (left_screen_x, floor_y),
        (right_screen_x, floor_y),
        wall_width
    )

    for px in partitions:
        x = helpers.to_screen(px, 0)[0]
        pygame.draw.line(screen, settings.PARTITION_COLOR, (x, floor_y), (x, top_y), partition_width)

    font = pygame.font.SysFont(None, settings.SMALL_FONT_SIZE)
    bin_width = helpers.get_bin_width()

    for i, count in enumerate(bin_counts):
        center_x = left_x + (i + 0.5) * bin_width
        sx, sy = helpers.to_screen(center_x, settings.PARTITION_HEIGHT * 0.5)
        text = font.render(str(count), True, settings.TEXT_COLOR)
        text_rect = text.get_rect(center=(sx, sy))
        screen.blit(text, text_rect)


# Draw HUD text
def draw_hud(screen, font, spawned_balls, landed_balls, paused):
    active_balls = spawned_balls - landed_balls

    lines = [
        f"Total Balls: {settings.TOTAL_BALLS}",
        f"Spawned: {spawned_balls}",
        f"Landed: {landed_balls}",
        f"Active: {active_balls}",
        f"Rows: {settings.PEG_ROWS}",
        f"Bins: {settings.BIN_COUNT}",
        f"Ball Radius: {settings.BALL_RADIUS}",
        f"Peg Radius: {settings.PEG_RADIUS}",
        f"Gravity: {settings.GRAVITY}",
        f"dt: {settings.DT * 1000:.2f} ms",
        f"Spawn Interval: {settings.SPAWN_INTERVAL_STEPS * settings.DT * 1000:.2f} ms",
        f"Paused: {'Yes' if paused else 'No'}",
        f"Pause: Space",
        f"Quit: ESC",
    ]

    x = 10
    y = 10

    for line in lines:
        text = font.render(line, True, settings.TEXT_COLOR)
        screen.blit(text, (x, y))
        y += settings.FONT_SIZE + 4