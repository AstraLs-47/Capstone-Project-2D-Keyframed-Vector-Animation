"""
renderer.py
-----------
Background: Ethiopian battlefield scene (Image 2 reference).
  Layer 0: sky gradient (deep crimson/orange sunset)
  Layer 1: distant mountains
  Layer 2: Ancient Ethiopian fortress/cliff silhouette
  Layer 3: midground - banners, barricades, flags
  Layer 4: foreground - ground, rocks, spears, fire

HUD, debug skeleton, showcase overlay also here.
"""

import math
import os
import pygame
from utils import WHITE, BLACK, YELLOW, RED, GREEN, DARK_GRAY, GOLD, TEAL, transform_point, mat_identity

_bg_image = None
_bg_loaded = False

GROUND_Y = 470


def draw_background(surface, width, height):
    # ---- SKY: glowing sunset ----
    for y in range(GROUND_Y):
        t = y / GROUND_Y
        # Gradient from deep orange to bright yellow
        r = int(220 + (255 - 220) * t)
        g = int(60 + (220 - 60) * t)
        b = int(20 + (50 - 20) * t)
        pygame.draw.line(surface, (min(255,r), min(255,g), min(255,b)), (0, y), (width, y))

    # ---- SUN ----
    sun_x, sun_y = width // 2 + 150, 220
    for glow in range(4):
        radius = 120 - glow * 20
        alpha_c = (255, 180 + glow*15, 50 + glow*20)
        pygame.draw.circle(surface, alpha_c, (sun_x, sun_y), radius)
    pygame.draw.circle(surface, (255, 240, 150), (sun_x, sun_y), 60)

    # ---- DISTANT MOUNTAINS (layer 1) ----
    mountains = [
        [(-50, GROUND_Y),(60, GROUND_Y-160),(200, GROUND_Y)],
        [(100, GROUND_Y),(280, GROUND_Y-210),(460, GROUND_Y)],
        [(340, GROUND_Y),(540, GROUND_Y-190),(720, GROUND_Y)],
        [(580, GROUND_Y),(740, GROUND_Y-170),(920, GROUND_Y)],
    ]
    for i, m in enumerate(mountains):
        shade = 38 + i*4
        pygame.draw.polygon(surface, (shade, shade//2, shade//3), m)

    # ---- FORTRESS/CLIFF SILHOUETTE (layer 2) ----
    # Ancient Ethiopian fortress on the left cliff
    fortress_pts = [
        (0, GROUND_Y), (0, GROUND_Y-240),
        (20, GROUND_Y-240), (20, GROUND_Y-270),
        (40, GROUND_Y-270), (40, GROUND_Y-240),
        (80, GROUND_Y-240), (80, GROUND_Y-280),
        (100,GROUND_Y-280),(100,GROUND_Y-240),
        (140,GROUND_Y-240),(140,GROUND_Y-265),
        (160,GROUND_Y-265),(160,GROUND_Y-240),
        (200,GROUND_Y-240),(200,GROUND_Y-200),
        (250,GROUND_Y-200),(250,GROUND_Y),
    ]
    pygame.draw.polygon(surface, (52, 38, 28), fortress_pts)
    # Fortress windows (arrow slits)
    for wx in [30, 70, 110, 150]:
        pygame.draw.rect(surface, (20,14,10), (wx, GROUND_Y-235, 6, 14))
    # Fortress wall detail lines
    for wy in range(GROUND_Y-235, GROUND_Y-180, 18):
        pygame.draw.line(surface, (62, 46, 34), (0, wy), (200, wy), 1)

    # ---- CLOSER HILLS (layer 3) ----
    hills = [
        [(0, GROUND_Y),(110, GROUND_Y-95),(250, GROUND_Y)],
        [(200,GROUND_Y),(420, GROUND_Y-110),(640, GROUND_Y)],
        [(560,GROUND_Y),(700, GROUND_Y-88),(900, GROUND_Y)],
    ]
    for h in hills:
        pygame.draw.polygon(surface, (68, 50, 38), h)

    # ---- ETHIOPIAN FLAGS (midground) ----
    banners = [
        (320, GROUND_Y-10, GROUND_Y-130, True),
        (480, GROUND_Y-10, GROUND_Y-110, False),
        (650, GROUND_Y-10, GROUND_Y-125, True),
    ]
    for bx, by, btop, flip in banners:
        # Flag pole
        pygame.draw.line(surface, (55, 38, 20), (bx, by), (bx, btop), 3)
        # Ethiopian flag: green top, yellow middle, red bottom (horizontal stripes)
        flag_w = 54
        flag_h = 30
        if flip:
            fx = bx - flag_w
        else:
            fx = bx
        fy = btop
        stripe_h = flag_h // 3
        # Green stripe (top)
        pygame.draw.rect(surface, (0, 140, 30), (fx, fy, flag_w, stripe_h))
        # Yellow stripe (middle)
        pygame.draw.rect(surface, (255, 210, 0), (fx, fy + stripe_h, flag_w, stripe_h))
        # Red stripe (bottom)
        pygame.draw.rect(surface, (200, 20, 20), (fx, fy + stripe_h*2, flag_w, stripe_h))
        # Blue circle in center
        cx = fx + flag_w // 2
        cy = fy + flag_h // 2
        pygame.draw.circle(surface, (0, 80, 180), (cx, cy), 9)
        # Star of Solomon (6-point star) on the circle
        for i in range(6):
            angle_outer = math.radians(i * 60 - 90)
            angle_inner = math.radians(i * 60 - 90 + 30)
            ox2 = cx + int(math.cos(angle_outer) * 8)
            oy2 = cy + int(math.sin(angle_outer) * 8)
            ix2 = cx + int(math.cos(angle_inner) * 4)
            iy2 = cy + int(math.sin(angle_inner) * 4)
            pygame.draw.line(surface, (255, 210, 0), (cx, cy), (ox2, oy2), 1)
        # Draw star outline
        star_pts = []
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            r = 8 if i % 2 == 0 else 4
            star_pts.append((cx + int(math.cos(angle)*r), cy + int(math.sin(angle)*r)))
        pygame.draw.polygon(surface, (255, 210, 0), star_pts, 1)
        # Flag border
        pygame.draw.rect(surface, (30, 20, 10), (fx, fy, flag_w, flag_h), 1)

    # ---- GROUND ----
    pygame.draw.rect(surface, (72, 52, 36), (0, GROUND_Y, width, height-GROUND_Y))
    pygame.draw.rect(surface, (55, 38, 25), (0, GROUND_Y, width, 14))

    # Ground texture dots
    for gx in range(0, width, 28):
        for gy_off in [4, 10]:
            pygame.draw.circle(surface, (62, 44, 30), (gx + (gy_off*3)%20, GROUND_Y+gy_off), 2)

    # ---- FOREGROUND ELEMENTS ----
    # Spears stuck in ground
    spear_locs = [(85,GROUND_Y-2), (105,GROUND_Y-2,-12),
                  (720,GROUND_Y-2,8), (745,GROUND_Y-2)]
    for i, sl in enumerate(spear_locs):
        sx, sy = sl[0], sl[1]
        angle = sl[2] if len(sl)>2 else 0
        dx = math.sin(math.radians(angle)) * 55
        pygame.draw.line(surface, (90,62,22), (sx,sy), (int(sx+dx), sy-55), 3)
        # Tip
        tip_x = int(sx+dx)
        tip_y = sy-55
        pygame.draw.polygon(surface, (160,160,165),
                             [(tip_x,tip_y-14),(tip_x+4,tip_y),(tip_x-4,tip_y)])

    # Rocks
    rock_data = [(140,GROUND_Y+5,24,14),(160,GROUND_Y+3,16,10),
                 (680,GROUND_Y+5,20,12),(700,GROUND_Y+3,14,9)]
    for rx,ry,rw,rh in rock_data:
        pygame.draw.ellipse(surface, (80,60,44), (rx-rw//2, ry-rh//2, rw, rh))
        pygame.draw.ellipse(surface, (65,48,34), (rx-rw//2, ry-rh//2, rw, rh), 1)

    # Fire / torches
    fire_positions = [(155,GROUND_Y-2),(520,GROUND_Y-2),(705,GROUND_Y-2)]
    tick = pygame.time.get_ticks() / 120.0
    for fx, fy in fire_positions:
        # flickering base
        flicker = math.sin(tick + fx*0.1) * 3
        # outer flame
        for layer, (fc, fh) in enumerate([((200,70,15),20),((230,110,20),14),((255,170,30),8)]):
            fpts = [
                (fx-6+layer, fy),
                (fx + math.sin(tick*1.3+layer)*2, fy - fh - flicker),
                (fx+6-layer, fy)
            ]
            pygame.draw.polygon(surface, fc, [(int(p[0]),int(p[1])) for p in fpts])

    # ---- SMOKE COLUMNS ----
    for sx, sy in [(155,GROUND_Y-18),(520,GROUND_Y-18),(705,GROUND_Y-18)]:
        for off in range(0, 80, 16):
            smoke_x = sx + math.sin(off*0.08 + tick*0.2)*5
            smoke_y = sy - off
            rad = 7 + off*0.18
            shade = min(65, 38 + off//3)
            pygame.draw.circle(surface, (shade, shade-4, shade-6),
                                (int(smoke_x), int(smoke_y)), int(rad))


SIDE_PANEL_W = 200

def draw_hud(surface, font, small_font, t, scene_name, debug_on, showcase_on,
             projection_mode="Orthographic", cam_zoom=1.0, obj_scale=1.0):
    w = surface.get_width()
    h = surface.get_height()
    panel_x = w - SIDE_PANEL_W

    # Semi-transparent dark panel background
    panel = pygame.Surface((SIDE_PANEL_W, h), pygame.SRCALPHA)
    panel.fill((20, 12, 8, 210))
    surface.blit(panel, (panel_x, 0))

    # Left border line
    pygame.draw.line(surface, (120, 80, 30), (panel_x, 0), (panel_x, h), 2)

    HEADING_COLOR = (220, 160, 30)   # gold
    TEXT_COLOR    = (220, 210, 190)  # warm white
    DIM_COLOR     = (160, 140, 110)  # muted

    y = 14
    margin = panel_x + 10

    def draw_section_title(label, yy):
        surface.blit(small_font.render(label, True, HEADING_COLOR), (margin, yy))
        pygame.draw.line(surface, (120, 80, 30), (margin, yy+16), (w-8, yy+16), 1)
        return yy + 22

    def draw_line(text, color, yy):
        surface.blit(small_font.render(text, True, color), (margin, yy))
        return yy + 17

    # ---- CAMERA ----
    y = draw_section_title("CAMERA", y)
    y = draw_line("Arrows = Pan",        TEXT_COLOR, y)
    y = draw_line("+/- = Zoom",          TEXT_COLOR, y)
    y = draw_line("V = Persp/Ortho",     TEXT_COLOR, y)
    y = draw_line("Mouse Drag",          TEXT_COLOR, y)
    y = draw_line("  = Rotate View",     DIM_COLOR,  y)
    y += 6

    # ---- WARRIOR ----
    y = draw_section_title("WARRIOR", y)
    y = draw_line("I/J/K/L = Move",  TEXT_COLOR, y)
    y = draw_line("U/O = Rotate",    TEXT_COLOR, y)
    y = draw_line("N/M = Scale",     TEXT_COLOR, y)
    y += 6

    # ---- OTHER ----
    y = draw_section_title("OTHER", y)
    y = draw_line("D = Debug",      TEXT_COLOR, y)
    y = draw_line("S = Showcase",   TEXT_COLOR, y)
    y = draw_line("SPACE = Pause",  TEXT_COLOR, y)
    y = draw_line("R = Restart",    TEXT_COLOR, y)
    y = draw_line("ESC = Exit",     TEXT_COLOR, y)
    y += 6

    # ---- STATUS ----
    y = draw_section_title("STATUS", y)
    minutes, secs = divmod(int(t), 60)
    y = draw_line(f"{minutes}:{secs:02d} / 1:30",      TEXT_COLOR, y)
    y = draw_line(scene_name,                            HEADING_COLOR, y)
    y = draw_line(f"Proj: {projection_mode}",           DIM_COLOR, y)
    y = draw_line(f"Zoom: {cam_zoom:.2f}",              DIM_COLOR, y)
    y = draw_line(f"Scale: {obj_scale:.2f}",            DIM_COLOR, y)

    if debug_on or showcase_on:
        y += 4
        flags = []
        if debug_on:   flags.append("DEBUG ON")
        if showcase_on: flags.append("SHOWCASE")
        y = draw_line("  ".join(flags), (255, 80, 80), y)


def draw_debug_skeleton(surface, font, root_joint):
    for joint, parent in root_joint.walk():
        if "_geom" in joint.name or joint.name in ("shield", "spear"):
            continue

        ox, oy = joint.origin()
        
        # Color coding per user request
        circle_color = YELLOW
        if "shoulder" in joint.name:
            circle_color = (0, 0, 255)  # Blue circle = shoulder
        elif "elbow" in joint.name:
            circle_color = (0, 255, 0)  # Green circle = elbow
        elif "hand" in joint.name or "wrist" in joint.name:
            circle_color = (255, 0, 0)  # Red circle = wrist

        if parent is not None:
            # Don't draw line from parent if parent is a geometry node (should not happen with our setup)
            if not ("_geom" in parent.name or parent.name in ("shield", "spear")):
                px, py = parent.origin()
                
                # Highlight arm chains specifically as requested: Shoulder -> Elbow -> Wrist
                if ("shoulder" in parent.name and "elbow" in joint.name) or \
                   ("elbow" in parent.name and "hand" in joint.name):
                    pygame.draw.line(surface, circle_color, (int(px),int(py)), (int(ox),int(oy)), 4)
                else:
                    pygame.draw.line(surface, (200,200,200), (int(px),int(py)), (int(ox),int(oy)), 2)
                    pygame.draw.line(surface, RED, (int(px),int(py)), (int(ox),int(oy)), 1)

        radius = 6 if circle_color != YELLOW else 4
        pygame.draw.circle(surface, circle_color, (int(ox), int(oy)), radius)
        pygame.draw.circle(surface, BLACK,  (int(ox), int(oy)), radius, 1)
        
        label = f"{joint.name} ({joint.angle:.0f}°)"
        txt = font.render(label, True, (10,10,10), (255,255,255))
        surface.blit(txt, (int(ox)+8, int(oy)-10))


SHOWCASE_STEPS = [
    ("1. COMPOSITE OBJECT MODELING",
     "Torso joint draws: teal robe, fur cape, belt, cross decoration",
     "Shield on left_hand joint, Spear on right_hand joint.",
     "Each BodyPart has its own local geometry."),
    ("2. HIERARCHICAL FORWARD KINEMATICS",
     "World -> Torso -> {Neck->Head, Shoulders->Arms->Hands->Weapons,",
     "Hips->Thighs->Shins->Feet}. Rotating torso carries all children.",
     "Limbs always stay connected to their parent joint."),
    ("3. MATRIX TRANSFORMATIONS",
     "world_matrix = parent_matrix x T(offset) x R(angle) x S(scale)",
     "Only joint ANGLES change — no vertex editing anywhere.",
     "Debug skeleton shows every computed joint origin."),
    ("4. KEYFRAME INTERPOLATION (LERP)",
     "value = start + (end - start) * t",
     "Blending 'idle_guard' -> 'spear_thrust' live below:",
     ""),
    ("5. FULL ANIMATION",
     "6 scenes, 90 seconds, timer-based (dt-driven, FPS-independent).",
     "Walk cycle + step-back locomotion overlays + procedural breathing.",
     ""),
]
SHOWCASE_STEP_TIME = 6.0


def draw_showcase_overlay(surface, font, small_font, step_index, step_t):
    title, l1, l2, l3 = SHOWCASE_STEPS[step_index % len(SHOWCASE_STEPS)]
    panel = pygame.Surface((surface.get_width(), 95), pygame.SRCALPHA)
    panel.fill((255, 255, 255, 215))
    surface.blit(panel, (0, 56))

    surface.blit(font.render(title, True, (120, 20, 20)), (16, 60))
    for i, line in enumerate((l1, l2, l3)):
        if line:
            surface.blit(small_font.render(line, True, BLACK), (16, 84+i*18))

    if step_index % len(SHOWCASE_STEPS) == 3:
        t_val = (step_t / SHOWCASE_STEP_TIME) % 1.0
        bx, by, bw, bh = 16, 140, 320, 10
        pygame.draw.rect(surface, DARK_GRAY, (bx, by, bw, bh), 1)
        pygame.draw.rect(surface, GREEN, (bx, by, int(bw*t_val), bh))
        lbl = small_font.render(f"t = {t_val:.2f}   value = start + (end-start)*t", True, BLACK)
        surface.blit(lbl, (bx, by+14))
