"""
character.py
Ethiopian warrior rig. All geometry is drawn in LOCAL joint coordinates
and pushed through the FK world matrix — joints always stay connected.

"""
import math
import pygame

from utils import (
    WHITE, CREAM, SKIN, SKIN_DARK, BROWN, BROWN_DARK,
    TEAL, TEAL_DARK, GOLD, GOLD_DARK, FUR, FUR_DARK,
    SHIELD_RED, SHIELD_RIM, BELT_BROWN, SPEAR_WOOD, SPEAR_TIP,
    GREEN, YELLOW, RED, BLACK, DARK_GRAY,
    transform_points, transform_point, mat_uniform_scale,
)
from kinematics import Joint, BodyPart
import patterns as pat


# SEGMENT LENGTHS  (tweak to reproportion)

SHOULDER_Y   = 0
SHOULDER_X   = 26
TORSO_H      = 48   # torso height from pelvis origin up to shoulder/neck start
WAIST_H      = 18   # hip joints hang this far BELOW torso origin
HIP_X        = 15
NECK_H       = 13
HEAD_R       = 22
UPPER_ARM_L  = 48
FOREARM_L    = 44
HAND_R       = 8
THIGH_L      = 60
SHIN_L       = 54
FOOT_L       = 22


# PRIMITIVE HELPERS

def _poly(surface, matrix, pts, color, width=0):
    tp = transform_points(matrix, pts)
    if len(tp) >= 3:
        pygame.draw.polygon(surface, color, tp, width)

def _line(surface, matrix, p0, p1, color, w=3):
    a, b = transform_points(matrix, [p0, p1])
    pygame.draw.line(surface, color, (int(a[0]),int(a[1])), (int(b[0]),int(b[1])), max(1,w))

def _circle(surface, matrix, center, radius, color, width=0):
    pt = transform_point(matrix, center)
    rx = max(1, int(radius * math.hypot(matrix[0], matrix[1])))
    ry = max(1, int(radius * math.hypot(matrix[3], matrix[4])))
    if abs(rx - ry) <= 1:
        pygame.draw.circle(surface, color, (int(pt[0]), int(pt[1])), rx, width)
    else:
        rect = pygame.Rect(int(pt[0]-rx), int(pt[1]-ry), rx*2, ry*2)
        pygame.draw.ellipse(surface, color, rect, width)

def _rounded_rect(surface, matrix, x, y, w, h, color):
    """Draw a rounded rectangle by overlapping rect + two circles."""
    pts = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
    _poly(surface, matrix, pts, color)



# DRAW FUNCTIONS


def draw_torso(surface, matrix, extra):
    """
    Complete torso: cream robe, thick fur cape, teal sash, red belt.
    """
    # ---- ROBE BODY (Cream) ----
    robe_pts = [(-26, -TORSO_H), (26, -TORSO_H),
                (32,  WAIST_H+30), (-32, WAIST_H+30)]
    _poly(surface, matrix, robe_pts, CREAM)

    # Robe side seams
    _line(surface, matrix, (-26, -TORSO_H), (-32, WAIST_H+30), SKIN_DARK, 2)
    _line(surface, matrix, ( 26, -TORSO_H), ( 32, WAIST_H+30), SKIN_DARK, 2)

    # Teal border at the bottom hem
    hem_y = WAIST_H + 26
    _poly(surface, matrix,
          [(-32, hem_y), (32, hem_y), (33, hem_y+4), (-33, hem_y+4)],
          TEAL)

    # ---- FRONT SASH (Teal with Gold ornaments) ----
    if not extra.get("back_view", False):
        sash_pts = [(-12, -TORSO_H), (12, -TORSO_H), (10, WAIST_H+20), (-10, WAIST_H+20)]
        _poly(surface, matrix, sash_pts, TEAL)
        _line(surface, matrix, (-12, -TORSO_H), (-10, WAIST_H+20), TEAL_DARK, 2)
        _line(surface, matrix, ( 12, -TORSO_H), ( 10, WAIST_H+20), TEAL_DARK, 2)

        # Gold ornaments on the sash (horizontal bars / triangles)
        for y in [-40, -25, -10]:
            _poly(surface, matrix, [(-8, y), (8, y), (5, y+5), (-5, y+5)], GOLD)
            _poly(surface, matrix, [(-8, y), (8, y), (5, y+5), (-5, y+5)], GOLD_DARK, 1)

        # Bottom gold loop ornaments
        loop_y = WAIST_H + 10
        _circle(surface, matrix, (-6, loop_y), 5, GOLD, 3)
        _circle(surface, matrix, ( 6, loop_y), 5, GOLD, 3)

    # ---- BELT (Red with Brown Pouches) ----
    belt_y = -4
    _poly(surface, matrix,
          [(-27, belt_y-6), (27, belt_y-6), (27, belt_y+8), (-27, belt_y+8)],
          RED)
    
    if not extra.get("back_view", False):
        # Brown pouches on the belt
        for bx in [-18, -6, 6, 18]:
            _rounded_rect(surface, matrix, bx-4, belt_y-8, 8, 14, BELT_BROWN)
            _poly(surface, matrix, [(bx-4, belt_y-8), (bx+4, belt_y-8), (bx+4, belt_y+6), (bx-4, belt_y+6)], BLACK, 1)

    # Fur cape has been moved to its own joint so it draws OVER the arms


def draw_fur_cape(surface, matrix, extra):
    """Thick fur cape drawn over the torso and arms."""
    # Left fur mass (extended outward and downward)
    fur_l_pts = [
        (-15, -TORSO_H-8), (-55, -TORSO_H+5), (-60, -TORSO_H+45),
        (-48, -TORSO_H+65), (-35, -TORSO_H+60), (-20, -TORSO_H+25)
    ]
    _poly(surface, matrix, fur_l_pts, FUR)

    # Right fur mass
    fur_r_pts = [
        (15, -TORSO_H-8), (55, -TORSO_H+5), (60, -TORSO_H+45),
        (48, -TORSO_H+65), (35, -TORSO_H+60), (20, -TORSO_H+25)
    ]
    _poly(surface, matrix, fur_r_pts, FUR)

    # Center collar fur
    fur_c_pts = [(-20, -TORSO_H-8), (20, -TORSO_H-8), (25, -TORSO_H+15), (-25, -TORSO_H+15)]
    _poly(surface, matrix, fur_c_pts, FUR)

    # Fur tufts (procedural spiky look)
    def _tuft(bx, by, angle_deg, length):
        import math
        r = math.radians(angle_deg)
        ex = bx + math.cos(r)*length
        ey = by + math.sin(r)*length
        tuft_pts = [
            (bx - 3*math.sin(r), by + 3*math.cos(r)),
            (ex, ey),
            (bx + 3*math.sin(r), by - 3*math.cos(r)),
        ]
        _poly(surface, matrix, tuft_pts, FUR_DARK)

    tuft_data_l = [
        (-48,-TORSO_H+18,-150,16), (-50,-TORSO_H+28,-160,14),
        (-50,-TORSO_H+38,-170,16), (-46,-TORSO_H+46,-160,14),
        (-40,-TORSO_H+50,-140,13), (-32,-TORSO_H+50,-120,12),
    ]
    tuft_data_r = [
        (48,-TORSO_H+18,-30,16), (50,-TORSO_H+28,-20,14),
        (50,-TORSO_H+38,-10,16), (46,-TORSO_H+46,-20,14),
        (40,-TORSO_H+50,-40,13), (32,-TORSO_H+50,-60,12),
    ]
    for td in tuft_data_l + tuft_data_r:
        _tuft(*td)

    # Fur dark outline / texture lines
    _poly(surface, matrix, fur_l_pts, FUR_DARK, 2)
    _poly(surface, matrix, fur_r_pts, FUR_DARK, 2)
    _poly(surface, matrix, fur_c_pts, FUR_DARK, 2)

def draw_neck(surface, matrix, extra):
    _poly(surface, matrix,
          [(-7, 0), (7, 0), (6, -NECK_H), (-6, -NECK_H)],
          SKIN)


def draw_head(surface, matrix, extra):
    turn  = extra.get("turn", 0.0)
    blink = extra.get("blink", False)
    cy = -HEAD_R + 2

    # Large Afro Hair (bumpy black outline using overlapping circles)
    # Huge central mass
    _circle(surface, matrix, (0, cy-12), HEAD_R+16, BLACK)
    # Surrounding bumpy texture
    afro_pts = [
        (-28, cy+8), (-36, cy-2), (-35, cy-16), (-25, cy-32), 
        (-12, cy-40), (0, cy-42), (12, cy-40), (25, cy-32), 
        (35, cy-16), (36, cy-2), (28, cy+8)
    ]
    for hx, hy in afro_pts:
        _circle(surface, matrix, (hx, hy), 12, BLACK)

    # Head sphere
    _circle(surface, matrix, (0, cy), HEAD_R, SKIN)

    # Ears
    _circle(surface, matrix, (-HEAD_R+1, cy+2), 5, SKIN)
    _circle(surface, matrix, ( HEAD_R-1, cy+2), 5, SKIN)
    _circle(surface, matrix, (-HEAD_R+1, cy+2), 5, SKIN_DARK, 2)
    _circle(surface, matrix, ( HEAD_R-1, cy+2), 5, SKIN_DARK, 2)

    # Tri-color Headband (Green, Yellow, Red)
    band_y = cy - 10
    band_top = cy - 19
    band_m1 = cy - 13
    band_m2 = cy - 16
    
    # Green (top)
    _poly(surface, matrix, [(-HEAD_R-1, band_m2), (HEAD_R+1, band_m2), (HEAD_R+1, band_top), (-HEAD_R-1, band_top)], (20, 150, 40))
    # Yellow (middle)
    _poly(surface, matrix, [(-HEAD_R-1, band_m1), (HEAD_R+1, band_m1), (HEAD_R+1, band_m2), (-HEAD_R-1, band_m2)], (240, 200, 20))
    # Red (bottom)
    _poly(surface, matrix, [(-HEAD_R-1, band_y), (HEAD_R+1, band_y), (HEAD_R+1, band_m1), (-HEAD_R-1, band_m1)], (200, 20, 20))
    
    # Outline
    _poly(surface, matrix, [(-HEAD_R-1, band_y), (HEAD_R+1, band_y), (HEAD_R+1, band_top), (-HEAD_R-1, band_top)], DARK_GRAY, 1)

    if not extra.get("back_view", False):
        # Eyebrows
        _line(surface, matrix, (-11, cy-8), (-3, cy-7), BLACK, 2)
        _line(surface, matrix, ( 11, cy-8), ( 3, cy-7), BLACK, 2)

        # Eyes
        eye_dx = 7 + turn*3
        if blink:
            _line(surface, matrix, (-eye_dx-4, cy-2), (-eye_dx+4, cy-2), BLACK, 2)
            _line(surface, matrix, ( eye_dx-4, cy-2), ( eye_dx+4, cy-2), BLACK, 2)
        else:
            # Realistic eye left
            _poly(surface, matrix, [(-eye_dx-4, cy-1), (-eye_dx, cy-3), (-eye_dx+4, cy-1), (-eye_dx, cy+1)], WHITE)
            _circle(surface, matrix, (-eye_dx, cy-1), 2, BROWN_DARK)  # Iris
            _circle(surface, matrix, (-eye_dx, cy-1), 1, BLACK)       # Pupil
            _circle(surface, matrix, (-eye_dx+1, cy-2), 1, WHITE)     # Highlight
            # Thick upper eyelid
            _line(surface, matrix, (-eye_dx-4, cy-2), (-eye_dx, cy-4), BLACK, 2)
            _line(surface, matrix, (-eye_dx, cy-4), (-eye_dx+4, cy-2), BLACK, 2)
            
            # Realistic eye right
            _poly(surface, matrix, [(eye_dx-4, cy-1), (eye_dx, cy-3), (eye_dx+4, cy-1), (eye_dx, cy+1)], WHITE)
            _circle(surface, matrix, (eye_dx, cy-1), 2, BROWN_DARK)   # Iris
            _circle(surface, matrix, (eye_dx, cy-1), 1, BLACK)        # Pupil
            _circle(surface, matrix, (eye_dx+1, cy-2), 1, WHITE)      # Highlight
            # Thick upper eyelid
            _line(surface, matrix, (eye_dx-4, cy-2), (eye_dx, cy-4), BLACK, 2)
            _line(surface, matrix, (eye_dx, cy-4), (eye_dx+4, cy-2), BLACK, 2)

        # Nose
        _line(surface, matrix, (0, cy-5), (0, cy+4), SKIN_DARK, 2) # bridge
        _poly(surface, matrix, [(-3, cy+6), (3, cy+6), (0, cy+8)], SKIN_DARK) # tip/nostrils

        # Thin mustache
        _line(surface, matrix, (-5, cy+10), (5, cy+10), BLACK, 1)
        
        # Mouth (fuller lips)
        _poly(surface, matrix, [(-5, cy+12), (5, cy+12), (0, cy+10)], BROWN_DARK) # upper lip
        _poly(surface, matrix, [(-5, cy+12), (5, cy+12), (0, cy+14)], BROWN)      # lower lip

        # Beard (goatee below jaw)
        jaw_y = cy + HEAD_R*0.72
        beard_pts = [(-5, jaw_y),(5, jaw_y),(3, jaw_y+10),(0, jaw_y+16),(-3, jaw_y+10)]
        _poly(surface, matrix, beard_pts, BLACK)


def draw_upper_arm(surface, matrix, extra):
    """Upper arm: fully covered by cream sleeve with a curved shoulder cap."""
    # 1. Circle cap for the shoulder pivot (drawn first so bottom half is covered)
    _circle(surface, matrix, (0, 0), 10, CREAM)
    _circle(surface, matrix, (0, 0), 10, SKIN_DARK, 1)

    # 2. Main sleeve body starting from y=0
    sleeve_pts = [(-10, 0), (10, 0), (8, UPPER_ARM_L+2), (-8, UPPER_ARM_L+2)]
    _poly(surface, matrix, sleeve_pts, CREAM)
    
    # 3. Outline lines for the left, right, and bottom (leaving the top curve intact)
    _line(surface, matrix, (-10, 0), (-8, UPPER_ARM_L+2), SKIN_DARK, 1)
    _line(surface, matrix, (10, 0), (8, UPPER_ARM_L+2), SKIN_DARK, 1)
    _line(surface, matrix, (-8, UPPER_ARM_L+2), (8, UPPER_ARM_L+2), SKIN_DARK, 1)


def draw_forearm(surface, matrix, extra):
    # Cream sleeve covering the forearm
    pts = [(-6, 0), (6, 0), (5, FOREARM_L-5), (-5, FOREARM_L-5)]
    _poly(surface, matrix, pts, CREAM)
    
    # Teal cuff extending down to the hand
    cuff_pts = [(-5, FOREARM_L-5), (5, FOREARM_L-5), (5, FOREARM_L+2), (-5, FOREARM_L+2)]
    _poly(surface, matrix, cuff_pts, TEAL)
    
    _poly(surface, matrix, pts, SKIN_DARK, 1)
    _poly(surface, matrix, cuff_pts, SKIN_DARK, 1)


def draw_hand(surface, matrix, extra):
    _circle(surface, matrix, (0, HAND_R), HAND_R+1, SKIN)
    _circle(surface, matrix, (0, HAND_R), HAND_R+1, SKIN_DARK, 1)


def draw_shield(surface, matrix, extra):
    """
    Protector (Shield): Red face, gold rim with small dashes, gold star accents, pointed boss.
    """
    r = 42
    cx, cy = 0, 0
    
    # Outer gold rim
    _circle(surface, matrix, (cx, cy), r+3, GOLD)
    _circle(surface, matrix, (cx, cy), r+3, GOLD_DARK, 1)
    
    # Main red face
    _circle(surface, matrix, (cx, cy), r, SHIELD_RED)
    
    # Inner gold ring
    _circle(surface, matrix, (cx, cy), r-5, GOLD, 2)
    
    # Dashes on the outer red edge (between inner ring and outer rim)
    for i in range(24):
        angle = math.radians(i * 15)
        dx = math.cos(angle)
        dy = math.sin(angle)
        _line(surface, matrix, (cx + dx*(r-3), cy + dy*(r-3)), (cx + dx*r, cy + dy*r), GOLD, 2)

    # Four gold star/cross accents
    for angle_deg in [0, 90, 180, 270]:
        angle = math.radians(angle_deg + 45) # offset from center
        dx = math.cos(angle) * (r - 18)
        dy = math.sin(angle) * (r - 18)
        # Small diamond/star shape
        pts = [
            (cx + dx, cy + dy - 4), (cx + dx + 4, cy + dy),
            (cx + dx, cy + dy + 4), (cx + dx - 4, cy + dy)
        ]
        _poly(surface, matrix, pts, GOLD)

    # Pointed Center Boss
    _circle(surface, matrix, (cx, cy), 12, GOLD_DARK)
    _circle(surface, matrix, (cx, cy), 10, GOLD)
    # The pointed tip (drawn as a small bright polygon)
    tip_pts = [(cx-5, cy+3), (cx+5, cy+3), (cx, cy-8)]
    _poly(surface, matrix, tip_pts, WHITE)
    _circle(surface, matrix, (cx, cy), 4, WHITE)


def draw_spear(surface, matrix, extra):
    """
    Arrow (Spear): Silver tip, gold connector, twisted grip, gold bottom point.
    """
    shaft_top = -83
    shaft_bot =  67

    # Shaft (brown wood)
    _line(surface, matrix, (0, shaft_bot), (0, shaft_top), SPEAR_WOOD, 5)
    
    # Twisted grip just below the tip connector
    for gy in range(shaft_top + 10, shaft_top + 40, 4):
        _line(surface, matrix, (-3, gy), (3, gy+3), GOLD_DARK, 2)
        
    # Gold connector at the top
    _poly(surface, matrix, [(-4, shaft_top), (4, shaft_top), (3, shaft_top+10), (-3, shaft_top+10)], GOLD)

    # Silver spear tip (like an arrow)
    head_pts = [(0, shaft_top-35), (6, shaft_top-10), (4, shaft_top), (-4, shaft_top), (-6, shaft_top-10)]
    _poly(surface, matrix, head_pts, WHITE)
    _poly(surface, matrix, head_pts, DARK_GRAY, 1)
    # Central ridge of the tip
    _line(surface, matrix, (0, shaft_top-35), (0, shaft_top), DARK_GRAY, 1)

    # Gold point at the bottom (butt cap)
    _poly(surface, matrix, [(-3, shaft_bot-5), (3, shaft_bot-5), (0, shaft_bot+10)], GOLD)


def draw_thigh(surface, matrix, extra):
    """Thigh: cream trouser shows below the robe."""
    # Full leg in cream/trouser color
    pts = [(-10, 0), (10, 0), (8, THIGH_L), (-8, THIGH_L)]
    _poly(surface, matrix, pts, CREAM)
    
    # Robe overlay covering top of thigh (matches new cream robe color)
    robe_cover = [(-11, -2), (11, -2), (9, THIGH_L*0.40), (-9, THIGH_L*0.40)]
    _poly(surface, matrix, robe_cover, CREAM)
    # Teal hem line where robe ends
    _line(surface, matrix, (-10, THIGH_L*0.40), (10, THIGH_L*0.40), TEAL, 2)
    # Outline
    _poly(surface, matrix, pts, SKIN_DARK, 1)


def draw_shin(surface, matrix, extra):
    pts = [(-8, 0), (8, 0), (6, SHIN_L), (-6, SHIN_L)]
    _poly(surface, matrix, pts, CREAM)
    _poly(surface, matrix, pts, SKIN_DARK, 1)


def draw_foot(surface, matrix, extra):
    """Bare foot."""
    # Heel to toe
    pts = [(-7, -2), (FOOT_L-4, -2), (FOOT_L+2, 8), (-4, 6)]
    _poly(surface, matrix, pts, SKIN)
    
    # Toe lines
    _line(surface, matrix, (FOOT_L-2, 6), (FOOT_L+2, 6), SKIN_DARK, 1)
    _line(surface, matrix, (FOOT_L-4, 5), (FOOT_L, 5), SKIN_DARK, 1)
    
    _poly(surface, matrix, pts, SKIN_DARK, 1)


class WarriorRig:
    """
    Hierarchical joint skeleton.
    World -> Torso -> {Neck->Head, L-Arm chain, R-Arm chain, L-Leg chain, R-Leg chain}

    IMPORTANT FIX: shield is a child of left_hand, spear of right_hand.
    Their geometry extends outward from the hand pivot, so they always
    follow the hand regardless of pose.
    """

    def __init__(self):
        self.world = Joint("world")

        # Torso: origin at pelvis level, draws upward
        self.torso = Joint("torso", offset=(0, 0), draw_fn=draw_torso)

        # Neck & head chain
        self.neck = Joint("neck",   offset=(0, -TORSO_H),  draw_fn=draw_neck)
        self.head = Joint("head",   offset=(0, -NECK_H),   draw_fn=draw_head)
        self.neck.add(self.head)

        # ---- LEFT ARM (shield side) ----
        self.left_shoulder = Joint("left_shoulder", offset=(-SHOULDER_X, -TORSO_H + SHOULDER_Y))
        self.left_elbow    = Joint("left_elbow", offset=(0, UPPER_ARM_L))
        self.left_hand     = Joint("left_hand", offset=(0, FOREARM_L))
        
        self.left_upper_arm_geom = Joint("left_upper_arm_geom", offset=(0, 0), draw_fn=draw_upper_arm)
        self.left_forearm_geom   = Joint("left_forearm_geom", offset=(0, 0), draw_fn=draw_forearm)
        self.left_hand_geom      = Joint("left_hand_geom", offset=(0, 0), draw_fn=draw_hand)
        # Shield: center boss at (0,0) = hand grip. No additional offset needed;
        # the arm pose angles (shoulder 35°, elbow 90°) naturally place the
        # shield beside the chest. The shield inherits all parent transforms.
        self.left_shield         = Joint("shield", offset=(0, 0), draw_fn=draw_shield)

        self.left_shoulder.add(self.left_upper_arm_geom, self.left_elbow)
        self.left_elbow.add(self.left_forearm_geom, self.left_hand)
        self.left_hand.add(self.left_hand_geom, self.left_shield)

        # ---- RIGHT ARM (spear side) ----
        self.right_shoulder = Joint("right_shoulder", offset=(SHOULDER_X, -TORSO_H + SHOULDER_Y))
        self.right_elbow    = Joint("right_elbow", offset=(0, UPPER_ARM_L))
        self.right_hand     = Joint("right_hand", offset=(0, FOREARM_L))

        self.right_upper_arm_geom = Joint("right_upper_arm_geom", offset=(0, 0), draw_fn=draw_upper_arm)
        self.right_forearm_geom   = Joint("right_forearm_geom", offset=(0, 0), draw_fn=draw_forearm)
        self.right_hand_geom      = Joint("right_hand_geom", offset=(0, 0), draw_fn=draw_hand)
        self.right_spear          = Joint("spear", offset=(0, HAND_R), draw_fn=draw_spear)

        self.right_shoulder.add(self.right_upper_arm_geom, self.right_elbow)
        self.right_elbow.add(self.right_forearm_geom, self.right_hand)
        self.right_hand.add(self.right_hand_geom, self.right_spear)

        # ---- LEFT LEG ----
        self.left_hip   = Joint("left_hip",   offset=(-HIP_X, WAIST_H), draw_fn=draw_thigh)
        self.left_knee  = Joint("left_knee",  offset=(0, THIGH_L),      draw_fn=draw_shin)
        self.left_foot  = Joint("left_ankle", offset=(0, SHIN_L),        draw_fn=draw_foot)
        self.left_knee.add(self.left_foot)
        self.left_hip.add(self.left_knee)

        # ---- RIGHT LEG ----
        self.right_hip   = Joint("right_hip",   offset=(HIP_X, WAIST_H), draw_fn=draw_thigh)
        self.right_knee  = Joint("right_knee",  offset=(0, THIGH_L),     draw_fn=draw_shin)
        self.right_foot  = Joint("right_ankle", offset=(0, SHIN_L),       draw_fn=draw_foot)
        self.right_knee.add(self.right_foot)
        self.right_hip.add(self.right_knee)

        # ---- FUR CAPE (Drawn on top of everything) ----
        self.fur_cape = Joint("fur_cape", offset=(0, 0), draw_fn=draw_fur_cape)

        # Wire torso children
        self.torso.add(
            self.neck,
            self.left_shoulder, self.right_shoulder,
            self.left_hip,      self.right_hip,
        )
        self.world.add(self.torso)

        # Channel map: pose key -> joint
        self.channels = {
            "world_lean":      self.world,
            "torso_rot":       self.torso,
            "neck":            self.neck,
            "head_tilt":       self.head,
            "left_shoulder":   self.left_shoulder,
            "left_elbow":      self.left_elbow,
            "left_wrist":      self.left_hand,
            "right_shoulder":  self.right_shoulder,
            "right_elbow":     self.right_elbow,
            "right_wrist":     self.right_hand,
            "left_hip":        self.left_hip,
            "left_knee":       self.left_knee,
            "left_ankle":      self.left_foot,
            "right_hip":       self.right_hip,
            "right_knee":      self.right_knee,
            "right_ankle":     self.right_foot,
        }

    def apply_pose(self, pose, root_x, root_y,
                   breathe_scale=1.0, head_turn=0.0, blink=False, back_view=False, scale_x=1.0):
        for name, joint in self.channels.items():
            joint.angle = pose.get(name, 0.0)
        self.torso.scale = breathe_scale
        self.head.extra["turn"]      = head_turn
        self.head.extra["blink"]     = blink
        self.head.extra["back_view"] = back_view
        self.torso.extra["back_view"] = back_view
        self.world.offset = (root_x, root_y)
        self.world.angle = 0.0
        self.world.scale = 1.0
        self.world.update(IDENTITY)

        if scale_x != 1.0:
            from utils import mat_mult, mat_translate, mat_scale
            # Flip around the character's own X centre so the body stays in place
            flip = mat_mult(
                mat_translate(root_x, 0),
                mat_mult(mat_scale(scale_x, 1.0), mat_translate(-root_x, 0))
            )
            self.world.world_matrix = mat_mult(flip, self.world.world_matrix)
            for c in self.world.children:
                c.update(self.world.world_matrix)

    def apply_manual_affine(self, tx, ty, rotation_deg, uniform_scale, scale_x=1.0):
        """
        Apply interactive affine transform after animation pose.
        Order at the world joint: T(offset+tx,ty) * R(rot) * S(scale)
        Scale is uniform about the warrior pivot (feet), so the body does not drift.
        """
        px, py = self.world.offset
        self.world.offset = (px + tx, py + ty)
        self.world.angle = rotation_deg
        self.world.scale = uniform_scale
        self.world.update(IDENTITY)

        if scale_x != 1.0:
            from utils import mat_mult, mat_translate, mat_scale
            pivot_x = px + tx
            flip = mat_mult(
                mat_translate(pivot_x, 0),
                mat_mult(mat_scale(scale_x, 1.0), mat_translate(-pivot_x, 0))
            )
            self.world.world_matrix = mat_mult(flip, self.world.world_matrix)
            for c in self.world.children:
                c.update(self.world.world_matrix)


    def draw(self, surface):
        """
        Painter's algorithm — respects front/back view:
          Front view: Legs → Torso → Neck → Spear Arm → Shield Arm
          Back  view: Legs → Spear Arm → Shield Arm → Torso → Neck
        Arms are drawn before the torso in back view so the back of the
        robe occludes the shoulder joints naturally, matching the
        storyboard 'back view' frames.
        """
        back_view = self.torso.extra.get("back_view", False)

        self.right_hip.draw(surface)
        self.left_hip.draw(surface)

        if back_view:
            # Arms behind the torso body
            self.right_upper_arm_geom.draw(surface)
            self.right_elbow.draw(surface)
            self.left_upper_arm_geom.draw(surface)
            self.left_elbow.draw(surface)
            if self.torso.draw_fn:
                self.torso.draw_fn(surface, self.torso.world_matrix, self.torso.extra)
            self.neck.draw(surface)
        else:
            # Arms in front of the torso
            if self.torso.draw_fn:
                self.torso.draw_fn(surface, self.torso.world_matrix, self.torso.extra)
            self.neck.draw(surface)
            self.right_upper_arm_geom.draw(surface)
            self.right_elbow.draw(surface)
            self.left_upper_arm_geom.draw(surface)
            self.left_elbow.draw(surface)

from utils import mat_identity
IDENTITY = mat_identity()
