import math
from utils import lerp_pose, lerp, clamp
from keyframes import POSES, WALK_CYCLE, WALK_BACK_CYCLE, RUN_CYCLE

TOTAL_DURATION = 90.0

SCENES = [
    (0.0,   10.0,  "Idle / Neutral"),
    (10.0,  25.0,  "Defend"),
    (25.0,  42.0,  "Attack"),
    (42.0,  57.0,  "Walk Forward"),
    (57.0,  77.0,  "Walk Back"),
    (77.0,  90.0,  "Victory / Reset"),
]

WALK_FORWARD_DIST = 280.0
WALK_CYCLE_PERIOD = 0.90


class Timeline:
    def __init__(self, checkpoints):
        self.checkpoints = sorted(checkpoints, key=lambda c: c[0])

    def sample(self, t):
        cps = self.checkpoints
        if t <= cps[0][0]:
            return dict(POSES[cps[0][1]])
        if t >= cps[-1][0]:
            return dict(POSES[cps[-1][1]])
        for i in range(len(cps) - 1):
            t0, name0 = cps[i]
            t1, name1 = cps[i + 1]
            if t0 <= t <= t1:
                frac = (t - t0) / (t1 - t0) if t1 > t0 else 1.0
                return lerp_pose(POSES[name0], POSES[name1], frac)
        return dict(POSES[cps[-1][1]])


MASTER_TIMELINE = Timeline([
    # ---- IDLE 0.0-10.0 ----
    (0.0,   "guard_stop"),
    (5.0,   "idle_inhale"),
    (10.0,  "guard_stop"),

    # ---- DEFENSE 10.0-25.0  (5 poses × 3 s each) ----
    (10.0,  "def_ready"),
    (12.5,  "def_lift"),
    (15.5,  "def_guard"),
    (20.0,  "def_hold"),
    (23.0,  "def_lower"),
    (25.0,  "guard_stop"),

    # ---- ATTACK 25.0-42.0  (5 poses, smooth pacing) ----
    (25.0,  "atk_ready"),
    (27.5,  "atk_windup"),
    (30.5,  "atk_step"),
    (33.5,  "atk_thrust_ext"),
    (36.0,  "atk_thrust_ext"),
    (39.0,  "atk_recovery"),
    (42.0,  "guard_stop"),

    # Walk Forward 42-57
    (42.0,  "walk_contact_l"),
    (57.0,  "walk_contact_l"),

    # Walk Back 57-77
    (57.0,  "walk_contact_l"),
    (77.0,  "walk_contact_l"),

    # ---- VICTORY 77.0-90.0 ----
    (77.0,  "guard_stop"),
    (79.0,  "victory_raise_arm"),
    (82.0,  "victory_shield_up"),
    (85.0,  "victory_look_up"),
    (88.0,  "victory_hold"),
    (90.0, "guard_stop"),
])


def _cycle_pose(cycle, period, t_local):
    """Sample a named pose cycle at local time t_local."""
    n = len(cycle)
    phase_len = period / n
    local = t_local % period
    idx = int(local // phase_len)
    frac = (local % phase_len) / phase_len
    a = POSES[cycle[idx % n]]
    b = POSES[cycle[(idx + 1) % n]]
    return lerp_pose(a, b, frac)


def get_scene_name(t):
    for start, end, name in SCENES:
        if start <= t < end:
            return name
    return SCENES[-1][2]


def evaluate(t: float):
    """
    Returns (pose_dict, root_x, root_y, breathe_scale, head_turn, blink, back_view, scale_x)
    """
    t = t % TOTAL_DURATION

    pose = MASTER_TIMELINE.sample(t)
    root_x, root_y = 0.0, 0.0
    back_view = False
    scale_x = 1.0

    # ---- WALK FORWARD  42.0 – 57.0  (15 s) ----
    if 42.0 <= t < 57.0:
        local_t  = t - 42.0
        progress = local_t / 15.0
        root_x   = lerp(0.0, WALK_FORWARD_DIST, progress)

        walk_pose = _cycle_pose(WALK_CYCLE, WALK_CYCLE_PERIOD, local_t)
        for k in ("left_hip",  "left_knee",  "left_ankle",
                  "right_hip", "right_knee", "right_ankle",
                  "left_shoulder",  "left_elbow",  "left_wrist",
                  "right_shoulder", "right_elbow", "right_wrist",
                  "world_lean"):
            pose[k] = walk_pose[k]

        bob = (local_t % WALK_CYCLE_PERIOD) / WALK_CYCLE_PERIOD
        root_y = -abs(math.sin(bob * math.pi * 2)) * 4.0

    # ---- WALK BACK  57.0 – 77.0  (20 s) ----
    elif 57.0 <= t < 77.0:
        local_t  = t - 57.0
        progress = local_t / 20.0
        root_x   = lerp(WALK_FORWARD_DIST, 0.0, progress)
        scale_x  = -1.0   # mirrored — warrior now faces left

        walk_back_pose = _cycle_pose(WALK_BACK_CYCLE, WALK_CYCLE_PERIOD, local_t)
        for k in ("left_hip",  "left_knee",  "left_ankle",
                  "right_hip", "right_knee", "right_ankle",
                  "left_shoulder",  "left_elbow",  "left_wrist",
                  "right_shoulder", "right_elbow", "right_wrist",
                  "world_lean"):
            pose[k] = walk_back_pose[k]

        # When mirrored (scale_x=-1), right_shoulder negative = spear pointing INTO body.
        # Clamp right_shoulder to >= 0 so spear always points away (forward in mirrored space)
        if pose.get("right_shoulder", 0) < 0:
            pose["right_shoulder"] = abs(pose.get("right_shoulder", 0)) * 0.3
        # Keep right_wrist neutral so spear tip stays upward/outward
        pose["right_wrist"] = 0.0

        bob = (local_t % WALK_CYCLE_PERIOD) / WALK_CYCLE_PERIOD
        root_y = -abs(math.sin(bob * math.pi * 2)) * 4.0

    # Victory / Reset: character returns to origin facing right
    elif t >= 77.0:
        root_x = 0.0

    # ---- Procedural overlays ----
    breathe_scale = 1.0 + 0.018 * math.sin(t * (2 * math.pi / 3.2))
    blink = (t % 4.5) < 0.12
    head_turn = 0.0

    return pose, root_x, root_y, breathe_scale, head_turn, blink, back_view, scale_x
