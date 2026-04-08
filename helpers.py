# helpers.py

import math
import random
import matplotlib.pyplot as plt
import numpy as np

import settings


# Convert simulation coordinates to screen coordinates
def to_screen(x, y):
    screen_x = settings.SCREEN_WIDTH / 2 + x * settings.PIXELS_PER_METER
    screen_y = settings.SCREEN_HEIGHT - y * settings.PIXELS_PER_METER
    return int(screen_x), int(screen_y)


# Convert length to pixels
def to_pixels(length):
    return int(length * settings.PIXELS_PER_METER)


# Clamp value between bounds
def clamp(value, low, high):
    return max(low, min(value, high))


# Closest point on a line segment
def closest_point_on_segment(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1

    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return x1, y1

    t = ((px - x1) * dx + (py - y1) * dy) / length_sq
    t = clamp(t, 0.0, 1.0)

    cx = x1 + t * dx
    cy = y1 + t * dy
    return cx, cy


# X-value on a line at a given y-value
def x_on_line_at_y(x1, y1, x2, y2, y):
    if abs(y2 - y1) < 1e-12:
        return x1

    t = (y - y1) / (y2 - y1)
    return x1 + t * (x2 - x1)


# Triangle wall geometry
def get_wall_geometry():
    apex_x = 0.0
    apex_y = settings.TRIANGLE_TOP_Y

    bottom_count = settings.PEG_ROWS
    bottom_width = (bottom_count - 1) * settings.PEG_HORIZONTAL_SPACING
    bottom_start_x = -bottom_width / 2

    left_bottom_peg_x = bottom_start_x
    right_bottom_peg_x = bottom_start_x + (bottom_count - 1) * settings.PEG_HORIZONTAL_SPACING
    bottom_peg_y = settings.TOP_MARGIN + settings.PEG_VERTICAL_SPACING

    offset = settings.PEG_RADIUS + settings.OUTER_WALL_GAP

    # Left wall
    left_dx = left_bottom_peg_x - apex_x
    left_dy = bottom_peg_y - apex_y
    left_len = math.sqrt(left_dx * left_dx + left_dy * left_dy)

    left_nx = left_dy / left_len
    left_ny = -left_dx / left_len

    left_apex_x = apex_x + left_nx * offset
    left_apex_y = apex_y + left_ny * offset
    left_bottom_x = left_bottom_peg_x + left_nx * offset
    left_bottom_y = bottom_peg_y + left_ny * offset

    # Right wall
    right_dx = right_bottom_peg_x - apex_x
    right_dy = bottom_peg_y - apex_y
    right_len = math.sqrt(right_dx * right_dx + right_dy * right_dy)

    right_nx = -right_dy / right_len
    right_ny = right_dx / right_len

    right_apex_x = apex_x + right_nx * offset
    right_apex_y = apex_y + right_ny * offset
    right_bottom_x = right_bottom_peg_x + right_nx * offset
    right_bottom_y = bottom_peg_y + right_ny * offset

    left_wall_x = x_on_line_at_y(
        left_apex_x, left_apex_y,
        left_bottom_x, left_bottom_y,
        settings.LOWER_SIDE_WALL_TOP_Y
    )

    right_wall_x = x_on_line_at_y(
        right_apex_x, right_apex_y,
        right_bottom_x, right_bottom_y,
        settings.LOWER_SIDE_WALL_TOP_Y
    )

    return {
        "left_apex_x": left_apex_x,
        "right_apex_x": right_apex_x,
        "left_wall_x": left_wall_x,
        "right_wall_x": right_wall_x,
    }


# Board wall segments
def get_wall_segments():
    geom = get_wall_geometry()

    left_segments = [
        (
            geom["left_apex_x"],
            settings.TRIANGLE_TOP_Y,
            geom["left_wall_x"],
            settings.LOWER_SIDE_WALL_TOP_Y
        ),
        (
            geom["left_wall_x"],
            settings.LOWER_SIDE_WALL_TOP_Y,
            geom["left_wall_x"],
            0.0
        )
    ]

    right_segments = [
        (
            geom["right_apex_x"],
            settings.TRIANGLE_TOP_Y,
            geom["right_wall_x"],
            settings.LOWER_SIDE_WALL_TOP_Y
        ),
        (
            geom["right_wall_x"],
            settings.LOWER_SIDE_WALL_TOP_Y,
            geom["right_wall_x"],
            0.0
        )
    ]

    return left_segments + right_segments


# Board bounds for bins
def get_board_bounds():
    geom = get_wall_geometry()
    return geom["left_wall_x"], geom["right_wall_x"]


# Width of each bin
def get_bin_width():
    left_x, right_x = get_board_bounds()
    return (right_x - left_x) / settings.BIN_COUNT


# Generate vertical partition positions
def generate_partitions():
    partitions = []
    left_x, _ = get_board_bounds()
    bin_width = get_bin_width()

    for i in range(1, settings.BIN_COUNT):
        x = left_x + i * bin_width
        partitions.append(x)

    return partitions


# Get bin index from x-position
def get_bin_index(x):
    left_x, right_x = get_board_bounds()
    bin_width = (right_x - left_x) / settings.BIN_COUNT

    index = int((x - left_x) / bin_width)
    return clamp(index, 0, settings.BIN_COUNT - 1)


# Generate triangular peg layout (skip top 2 rows)
def generate_pegs():
    pegs = []

    for row in range(2, settings.PEG_ROWS):
        peg_count = row + 1
        row_width = (peg_count - 1) * settings.PEG_HORIZONTAL_SPACING

        start_x = -row_width / 2
        y = settings.TOP_MARGIN + (settings.PEG_ROWS - row) * settings.PEG_VERTICAL_SPACING

        for col in range(peg_count):
            x = start_x + col * settings.PEG_HORIZONTAL_SPACING
            pegs.append((x, y))

    return pegs


# Random spawn inside triangle near the top
def random_spawn_position():
    geom = get_wall_geometry()

    spawn_y = settings.TRIANGLE_TOP_Y - 0.15

    left_x = x_on_line_at_y(
        geom["left_apex_x"], settings.TRIANGLE_TOP_Y,
        geom["left_wall_x"], settings.LOWER_SIDE_WALL_TOP_Y,
        spawn_y
    )

    right_x = x_on_line_at_y(
        geom["right_apex_x"], settings.TRIANGLE_TOP_Y,
        geom["right_wall_x"], settings.LOWER_SIDE_WALL_TOP_Y,
        spawn_y
    )

    spawn_x = random.uniform(left_x + settings.BALL_RADIUS, right_x - settings.BALL_RADIUS)
    return spawn_x, spawn_y


# Display final distribution graph
def show_distribution(bin_counts):
    x_vals = np.arange(len(bin_counts))
    y_vals = np.array(bin_counts)

    plt.figure()

    # Bar graph
    plt.bar(x_vals, y_vals, label="Simulation Data")

    # Compute mean and standard deviation
    total = np.sum(y_vals)
    mean = np.sum(x_vals * y_vals) / total
    variance = np.sum(y_vals * (x_vals - mean)**2) / total
    std_dev = np.sqrt(variance)

    # Create smooth curve 
    x_smooth = np.linspace(0, len(bin_counts) - 1, 300)

    y_smooth = (
        (1 / (std_dev * np.sqrt(2 * np.pi))) *
        np.exp(-0.5 * ((x_smooth - mean) / std_dev)**2)
    )

    # Scale to match histogram
    y_smooth *= total

    # Plot line of best fit
    plt.plot(x_smooth, y_smooth, color='red', linewidth=3, label="Normal Fit")

    # Labels
    plt.xlabel("Bin")
    plt.ylabel("Ball Count")
    plt.title("Plinko Distribution with Best Fit")
    plt.legend()

    plt.show()