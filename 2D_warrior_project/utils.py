"""
utils.py
Core math utilities: 3x3 homogeneous matrix pipeline (row-major).
Colors match the Ethiopian warrior reference: teal robe, fur cape,
gold trim, deep red shield, cream trousers, dark skin.
"""

import math

WHITE       = (245, 242, 235)
CREAM       = (232, 218, 180)
SKIN        = (101,  60,  30)     # rich dark brown skin
SKIN_DARK   = ( 72,  40,  16)     # shadow / darker skin areas
BROWN       = (101,  60,  30)     # kept for back-compat
BROWN_DARK  = ( 72,  40,  16)
TEAL        = ( 22,  80,  90)     # robe main color
TEAL_DARK   = ( 14,  58,  68)     # robe shadow
GOLD        = (200, 146,  42)     # trim / patterns
GOLD_DARK   = (140,  98,  20)
FUR         = (196, 163,  90)     # shoulder cape
FUR_DARK    = (140, 110,  50)
SHIELD_RED  = (120,  28,  28)     # shield face
SHIELD_RIM  = ( 80,  15,  15)
BELT_BROWN  = ( 88,  48,  16)
SPEAR_WOOD  = (120,  88,  20)
SPEAR_TIP   = (180, 180, 185)
GREEN       = ( 33, 110,  60)     # flag stripe
YELLOW      = (226, 178,  34)     # flag stripe / pattern
RED         = (160,  30,  28)     # flag stripe / pattern
BLACK       = ( 20,  18,  16)
DARK_GRAY   = ( 58,  58,  60)
BG_SKY      = ( 40,  20,  10)
BG_GROUND   = ( 80,  55,  35)

# MATRIX CONSTRUCTORS  (3x3 homogeneous, row-major stored as 9-tuple)

def mat_identity():
    return (1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0)

def mat_translate(tx, ty):
    return (1.0, 0.0, tx,
            0.0, 1.0, ty,
            0.0, 0.0, 1.0)

def mat_rotate(degrees):
    r = math.radians(degrees)
    c, s = math.cos(r), math.sin(r)
    return ( c, -s, 0.0,
             s,  c, 0.0,
             0.0, 0.0, 1.0)

def mat_scale(sx, sy):
    return (sx, 0.0, 0.0,
            0.0, sy,  0.0,
            0.0, 0.0, 1.0)

def mat_mult(a, b):
    a00,a01,a02,a10,a11,a12,a20,a21,a22 = a
    b00,b01,b02,b10,b11,b12,b20,b21,b22 = b
    return (
        a00*b00+a01*b10+a02*b20, a00*b01+a01*b11+a02*b21, a00*b02+a01*b12+a02*b22,
        a10*b00+a11*b10+a12*b20, a10*b01+a11*b11+a12*b21, a10*b02+a11*b12+a12*b22,
        a20*b00+a21*b10+a22*b20, a20*b01+a21*b11+a22*b21, a20*b02+a21*b12+a22*b22,
    )

def mat_chain(*mats):
    out = mat_identity()
    for m in mats:
        out = mat_mult(out, m)

# POINT TRANSFORMATION

def transform_point(m, p):
    x, y = p
    m00,m01,m02,m10,m11,m12,_,_,_ = m
    return (m00*x + m01*y + m02, m10*x + m11*y + m12)

def transform_points(m, pts):
    return [transform_point(m, p) for p in pts]

def mat_uniform_scale(m):
    return math.hypot(m[0], m[3])

# INTERPOLATION

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def lerp_pose(pose_a, pose_b, t):
    out = {}
    keys = set(pose_a.keys()) | set(pose_b.keys())
    for k in keys:
        a = pose_a.get(k, 0.0)
        b = pose_b.get(k, 0.0)
        out[k] = lerp(a, b, t)
    return out

def smoothstep(t):
    t = clamp(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)
