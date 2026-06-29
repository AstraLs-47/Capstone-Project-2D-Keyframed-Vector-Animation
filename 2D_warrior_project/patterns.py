import pygame
from utils import transform_points


def draw_diamond_grid(surface, matrix, x0, y0, width, height, rows, cols, color):
    """Procedurally tile a rectangular area with diamond (rhombus) shapes."""
    cell_w = width / cols
    cell_h = height / rows
    for row in range(rows):
        for col in range(cols):
            cx = x0 + col * cell_w + cell_w / 2
            cy = y0 + row * cell_h + cell_h / 2
            hw = cell_w * 0.36
            hh = cell_h * 0.36
            pts = [(cx, cy - hh), (cx + hw, cy), (cx, cy + hh), (cx - hw, cy)]
            pygame.draw.polygon(surface, color, transform_points(matrix, pts))


def draw_triangle_band(surface, matrix, x0, y0, width, height, count, color, point_up=True):
    """A horizontal band of repeating triangles (classic habesha hem trim)."""
    w = width / count
    for i in range(count):
        x = x0 + i * w
        if point_up:
            pts = [(x, y0 + height), (x + w / 2, y0), (x + w, y0 + height)]
        else:
            pts = [(x, y0), (x + w / 2, y0 + height), (x + w, y0)]
        pygame.draw.polygon(surface, color, transform_points(matrix, pts))


def draw_zigzag_border(surface, matrix, x0, y0, width, height, segments, color, thickness=3):
    """A zig-zag line generated from a loop over `segments` peaks/valleys."""
    seg_w = width / segments
    pts = []
    for i in range(segments + 1):
        x = x0 + i * seg_w
        y = y0 + (0 if i % 2 == 0 else height)
        pts.append((x, y))
    screen_pts = transform_points(matrix, pts)
    if len(screen_pts) >= 2:
        pygame.draw.lines(surface, color, False, screen_pts, thickness)


def draw_cross_motif(surface, matrix, cx, cy, size, color, thickness=3):
    """A simple cross / plus motif (common Ethiopian Orthodox-inspired
    decorative emblem, used here purely as a geometric pattern element)."""
    pts_v = [(cx, cy - size / 2), (cx, cy + size / 2)]
    pts_h = [(cx - size / 2, cy), (cx + size / 2, cy)]
    pygame.draw.lines(surface, color, False, transform_points(matrix, pts_v), thickness)
    pygame.draw.lines(surface, color, False, transform_points(matrix, pts_h), thickness)


def draw_cross_ring(surface, matrix, cx, cy, radius, count, size, color, thickness=2):
    """Loop a cross motif around a circle - used to decorate the shield."""
    import math
    for i in range(count):
        ang = (2 * math.pi / count) * i
        x = cx + radius * math.cos(ang)
        y = cy + radius * math.sin(ang)
        draw_cross_motif(surface, matrix, x, y, size, color, thickness)


def draw_dot_row(surface, matrix, x0, y0, width, count, radius, color):
    """A simple procedurally spaced row of dots (used as a trim accent)."""
    step = width / max(1, count - 1) if count > 1 else 0
    for i in range(count):
        x = x0 + i * step
        screen_pt = transform_points(matrix, [(x, y0)])[0]
        pygame.draw.circle(surface, color, (int(screen_pt[0]), int(screen_pt[1])), max(1, int(radius)))
