
CHANNELS = [
    "world_lean", "torso_rot", "neck",
    "left_shoulder", "left_elbow", "left_wrist",
    "right_shoulder", "right_elbow", "right_wrist",
    "left_hip", "left_knee", "left_ankle",
    "right_hip", "right_knee", "right_ankle",
]


def pose(base=None, **overrides):
    d = {k: 0.0 for k in CHANNELS}
    if base:
        d.update(base)
    d.update(overrides)
    return d

# BASE GUARD STANCE
# Matches image: symmetrical upright stance, shield on left side at chest
# level, spear held vertically on right side.

IDLE_GUARD = pose(
    world_lean=0,
    # Shield arm (left): upper arm angled outward ~30°, elbow ~85°
    # -> shield sits at left side of chest, fully visible, not covering face
    left_shoulder=30,
    left_elbow=85,
    left_wrist=0,
    # Spear arm (right): hangs nearly straight down, slight natural bend
    # -> spear points straight up beside the body
    right_shoulder=5,
    right_elbow=10,
    right_wrist=0,
    # Symmetrical legs (both feet under body, equal weight)
    left_hip=0,   left_knee=4,   left_ankle=-2,
    right_hip=0,  right_knee=4,  right_ankle=-2,
)


POSES = {

    # SCENE 1: Introduction / Idle
    
    "idle_guard":       IDLE_GUARD,
    "idle_inhale":      pose(IDLE_GUARD, torso_rot=-2, neck=-1),
    "idle_exhale":      pose(IDLE_GUARD, torso_rot=2,  neck=1),
    "head_scan_right":  pose(IDLE_GUARD, neck=20, torso_rot=4),
    "head_scan_left":   pose(IDLE_GUARD, neck=-20, torso_rot=-4),

    # SCENE 2: Walk cycle — 8 keyframes (contact/down/pass/up x 2)
    
    # --- LEFT foot contact (left leg extends forward) ---
    "walk_contact_l":  pose(IDLE_GUARD,
                             world_lean=2,
                             # Legs: left forward, right behind (angles reduced to stay in dress)
                             left_hip=-15,  left_knee=5,   left_ankle=5,
                             right_hip=15,  right_knee=20, right_ankle=-10,
                             # Arms
                             left_shoulder=28,  left_elbow=88,
                             right_shoulder=-25, right_elbow=20, right_wrist=-5),

    # --- DOWN pose (left foot plants, weight drops) ---
    "walk_down_l":     pose(IDLE_GUARD,
                             world_lean=2,
                             left_hip=-5,  left_knee=15,  left_ankle=5,
                             right_hip=10,  right_knee=15, right_ankle=-5,
                             left_shoulder=30,  left_elbow=90,
                             right_shoulder=-15, right_elbow=15, right_wrist=-5),

    # --- PASSING pose (left leg passes, right leg swings through) ---
    "walk_pass_l":     pose(IDLE_GUARD,
                             world_lean=1,
                             left_hip=5,   left_knee=20,  left_ankle=-10,
                             right_hip=2,  right_knee=5, right_ankle=2,
                             left_shoulder=32,  left_elbow=90,
                             right_shoulder=-5, right_elbow=10, right_wrist=0),

    # --- UP pose (body rises as right leg extends) ---
    "walk_up_l":       pose(IDLE_GUARD,
                             world_lean=2,
                             left_hip=10,  left_knee=15, left_ankle=-5,
                             right_hip=-8, right_knee=8, right_ankle=4,
                             left_shoulder=33,  left_elbow=90,
                             right_shoulder=5,  right_elbow=10, right_wrist=0),

    # --- RIGHT foot contact ---
    "walk_contact_r":  pose(IDLE_GUARD,
                             world_lean=2,
                             right_hip=-15, right_knee=5,  right_ankle=5,
                             left_hip=15,   left_knee=20,  left_ankle=-10,
                             left_shoulder=42,  left_elbow=88,
                             right_shoulder=25,  right_elbow=20, right_wrist=5),

    # --- DOWN right ---
    "walk_down_r":     pose(IDLE_GUARD,
                             world_lean=2,
                             right_hip=-5, right_knee=15, right_ankle=5,
                             left_hip=10,   left_knee=15,  left_ankle=-5,
                             left_shoulder=38,  left_elbow=90,
                             right_shoulder=15,  right_elbow=15, right_wrist=5),

    # --- PASSING right ---
    "walk_pass_r":     pose(IDLE_GUARD,
                             world_lean=1,
                             right_hip=5,  right_knee=20, right_ankle=-10,
                             left_hip=2,   left_knee=5,  left_ankle=2,
                             left_shoulder=36,  left_elbow=90,
                             right_shoulder=5,   right_elbow=10, right_wrist=0),

    # --- UP right ---
    "walk_up_r":       pose(IDLE_GUARD,
                             world_lean=2,
                             right_hip=10, right_knee=15, right_ankle=-5,
                             left_hip=-8, left_knee=8,  left_ankle=4,
                             left_shoulder=32,  left_elbow=90,
                             right_shoulder=-5, right_elbow=10, right_wrist=0),

    
    # SCENE 2: Run cycle — 8 keyframes
    # Forward torso lean, larger limb extension, shield stays stable
    
    "run_contact_l":   pose(IDLE_GUARD,
                             world_lean=8,
                             left_hip=-20,  left_knee=10,  left_ankle=5,
                             right_hip=25,  right_knee=40, right_ankle=-10,
                             left_shoulder=25,  left_elbow=85,
                             right_shoulder=-35, right_elbow=30, right_wrist=-10,
                             torso_rot=-5),

    "run_down_l":      pose(IDLE_GUARD,
                             world_lean=6,
                             left_hip=-10,  left_knee=25,  left_ankle=5,
                             right_hip=15,  right_knee=25, right_ankle=-5,
                             left_shoulder=28,  left_elbow=88,
                             right_shoulder=-20, right_elbow=25, right_wrist=-5,
                             torso_rot=-4),

    "run_pass_l":      pose(IDLE_GUARD,
                             world_lean=6,
                             left_hip=8,   left_knee=40,  left_ankle=-15,
                             right_hip=5,  right_knee=8, right_ankle=2,
                             left_shoulder=30,  left_elbow=88,
                             right_shoulder=-8,  right_elbow=20, right_wrist=-5,
                             torso_rot=-3),

    "run_flight_l":    pose(IDLE_GUARD,
                             world_lean=7,
                             left_hip=15,  left_knee=12, left_ankle=-4,
                             right_hip=-15, right_knee=10, right_ankle=4,
                             left_shoulder=32,  left_elbow=88,
                             right_shoulder=10,  right_elbow=15, right_wrist=0,
                             torso_rot=-4),

    "run_contact_r":   pose(IDLE_GUARD,
                             world_lean=8,
                             right_hip=-20, right_knee=10, right_ankle=5,
                             left_hip=25,   left_knee=40,  left_ankle=-10,
                             left_shoulder=40,  left_elbow=85,
                             right_shoulder=35,  right_elbow=30, right_wrist=10,
                             torso_rot=5),

    "run_down_r":      pose(IDLE_GUARD,
                             world_lean=6,
                             right_hip=-10, right_knee=25, right_ankle=5,
                             left_hip=15,   left_knee=25,  left_ankle=-5,
                             left_shoulder=36,  left_elbow=88,
                             right_shoulder=20,  right_elbow=25, right_wrist=5,
                             torso_rot=4),

    "run_pass_r":      pose(IDLE_GUARD,
                             world_lean=6,
                             right_hip=8,  right_knee=40, right_ankle=-15,
                             left_hip=5,   left_knee=8,  left_ankle=2,
                             left_shoulder=34,  left_elbow=88,
                             right_shoulder=8,   right_elbow=20, right_wrist=5,
                             torso_rot=3),

    "run_flight_r":    pose(IDLE_GUARD,
                             world_lean=7,
                             right_hip=15, right_knee=12, right_ankle=-4,
                             left_hip=-15, left_knee=10,  left_ankle=4,
                             left_shoulder=30,  left_elbow=88,
                             right_shoulder=-10, right_elbow=15, right_wrist=0,
                             torso_rot=4),

    
    # SCENE 3: ATTACK — Spear Thrust  (5 storyboard keyframes)
    # The spear moves ONLY FORWARD in a straight thrust.
    # Shield stays at the left side the entire time.
    # Feet stay grounded.  Arms remain connected to shoulders.
    
    # Pose 1 — READY: neutral, spear upright at right side, weight centred
    "atk_ready": pose(IDLE_GUARD,
                      right_shoulder=-25, right_elbow=75, right_wrist=-10),

    # Pose 2 — WIND UP: torso rotates back ~12°, spear arm pulled to hip,
    # right elbow heavily bent, spear remains pointing UP.
    "atk_windup": pose(IDLE_GUARD,
                       torso_rot=-12, world_lean=-3,
                       right_shoulder=15, right_elbow=90, right_wrist=-15,
                       left_shoulder=28, left_elbow=88,
                       right_hip=-5, left_hip=5),

    # Pose 3 — STEP / LEAN: step forward, arm begins extension,
    # wrist rotates so spear points FORWARD (horizontal).
    "atk_step": pose(IDLE_GUARD,
                     torso_rot=8, world_lean=6,
                     # shoulder(-20) + elbow(30) + wrist(-100) = -90 (horizontal right)
                     right_shoulder=-20, right_elbow=30, right_wrist=-100,
                     left_shoulder=30, left_elbow=88,
                     left_hip=14, left_knee=12, left_ankle=5,
                     right_hip=-8, right_knee=5),

    # Pose 4 — FULL EXTENSION / HIT: spear fully extended forward, contact frame.
    # Front knee bent, body leans into lunge, shield still at side.
    "atk_thrust_ext": pose(IDLE_GUARD,
                           torso_rot=15, world_lean=12,
                           # shoulder(-75) + elbow(5) + wrist(-20) = -90 (horizontal right)
                           right_shoulder=-75, right_elbow=5, right_wrist=-20,
                           left_shoulder=32, left_elbow=88,
                           left_hip=20, left_knee=22, left_ankle=6,
                           right_hip=-20, right_knee=6),

    # Pose 5 — RECOVERY: pull spear back, return upright
    "atk_recovery": pose(IDLE_GUARD,
                         torso_rot=-4, world_lean=2,
                         right_shoulder=0, right_elbow=60, right_wrist=-10,
                         left_shoulder=30, left_elbow=88),

    
    # SCENE 4: DEFENSE — Shield Block  (5 storyboard keyframes)
    # Shield protects torso + upper abdomen, NEVER covers the face.
    # Spear stays in ready position.  Only shoulder and elbow rotate.
    # Arms remain connected.  Smooth in/out transitions.

    # Pose 1 — READY: shield beside left torso, spear neutral, weight centred
    "def_ready": pose(IDLE_GUARD),

    # Pose 2 — LIFT SHIELD: rotate left shoulder up, bend elbow, raise shield
    # diagonally.  Spear arm stays neutral.
    "def_lift": pose(IDLE_GUARD,
                     left_shoulder=-18, left_elbow=80, left_wrist=0,
                     right_shoulder=5, right_elbow=10,
                     torso_rot=-3),

    # Pose 3 — GUARD POSITION: shield covers chest + upper abdomen; face visible.
    # Elbow pulled in, forearm angled across body.
    "def_guard": pose(IDLE_GUARD,
                      left_shoulder=-35, left_elbow=108, left_wrist=0,
                      right_shoulder=5, right_elbow=12,
                      torso_rot=-5, world_lean=-2,
                      left_hip=5, right_hip=-5),

    # Pose 4 — HOLD: maintain guard. Slight breathing motion only.
    "def_hold": pose(IDLE_GUARD,
                     left_shoulder=-34, left_elbow=106, left_wrist=0,
                     right_shoulder=5, right_elbow=12,
                     torso_rot=-5, world_lean=-2,
                     left_hip=5, right_hip=-5),

    # Pose 5 — LOWER SHIELD: rotate shoulder down, return to ready stance.
    "def_lower": pose(IDLE_GUARD,
                      left_shoulder=-10, left_elbow=88, left_wrist=0,
                      right_shoulder=5, right_elbow=10,
                      torso_rot=-2),

   
    # SCENE 5: Kept for compatibility (guard stances)
   
    "guard_stop":        pose(IDLE_GUARD),
    "raise_shield_mid":  pose(IDLE_GUARD,
                               left_shoulder=32, left_elbow=95,
                               torso_rot=-3),
    "raise_shield_full": pose(IDLE_GUARD,
                               left_shoulder=30, left_elbow=100,
                               torso_rot=-5),
    "look_left":         pose(IDLE_GUARD,
                               left_shoulder=30, left_elbow=100,
                               neck=-18, torso_rot=-5),
    "look_right":        pose(IDLE_GUARD,
                               left_shoulder=30, left_elbow=100,
                               neck=18, torso_rot=-5),
    "weight_shift_left": pose(IDLE_GUARD,
                               world_lean=-4, left_hip=-10, right_hip=14, torso_rot=-4),
    "weight_shift_right":pose(IDLE_GUARD,
                               world_lean=4,  left_hip=14, right_hip=-10, torso_rot=4),


    # SCENE 6: Victory
    # Spear raised overhead, shield held at waist/side (NOT covering face)
   
    "victory_raise_arm":  pose(IDLE_GUARD,
                                right_shoulder=-170, right_elbow=12, right_wrist=180,
                                left_shoulder=35, left_elbow=88,
                                torso_rot=-5, world_lean=-2),

    "victory_shield_up":  pose(IDLE_GUARD,
                                right_shoulder=-170, right_elbow=12, right_wrist=180,
                                left_shoulder=35,    left_elbow=88,
                                torso_rot=-5, world_lean=-2,
                                neck=-8),

    "victory_look_up":    pose(IDLE_GUARD,
                                right_shoulder=-170, right_elbow=12, right_wrist=180,
                                left_shoulder=35,    left_elbow=85,
                                neck=-12, torso_rot=-8, world_lean=-4),

    "victory_hold":       pose(IDLE_GUARD,
                                right_shoulder=-170, right_elbow=12, right_wrist=180,
                                left_shoulder=35,    left_elbow=85,
                                torso_rot=-8, world_lean=-4),

    # SCENE 7: Ending / Ceremonial

    "final_pose":       pose(IDLE_GUARD, torso_rot=-2),
    "ceremonial_guard": IDLE_GUARD,

    # TURN AROUND

    "turn_start": pose(IDLE_GUARD, torso_rot=8,  neck=12, world_lean=2),
    "turn_mid":   pose(IDLE_GUARD, torso_rot=20, neck=25, world_lean=4,
                       left_shoulder=22, left_elbow=80,
                       right_shoulder=8, right_elbow=18),
    "turn_end":   pose(IDLE_GUARD, torso_rot=0,  neck=0,  world_lean=-2),

    # WALK BACK — leg angles reduced to stay inside dress
  
    "walk_back_contact_l": pose(IDLE_GUARD, world_lean=-3,
                                 left_hip=-15, left_knee=5,   left_ankle=5,
                                 right_hip=15, right_knee=20, right_ankle=-8,
                                 left_shoulder=28, left_elbow=88,
                                 right_shoulder=-25, right_elbow=25),
    "walk_back_down_l":    pose(IDLE_GUARD, world_lean=-2,
                                 left_hip=-5,  left_knee=12, left_ankle=3,
                                 right_hip=10, right_knee=15, right_ankle=-4,
                                 left_shoulder=30, left_elbow=88,
                                 right_shoulder=-12, right_elbow=18),
    "walk_back_pass_l":    pose(IDLE_GUARD, world_lean=-1,
                                 left_hip=4,  left_knee=20, left_ankle=-8,
                                 right_hip=3, right_knee=6,  right_ankle=2,
                                 left_shoulder=32, left_elbow=88,
                                 right_shoulder=-5, right_elbow=15),
    "walk_back_up_l":      pose(IDLE_GUARD, world_lean=-2,
                                 left_hip=10,   left_knee=15, left_ankle=-4,
                                 right_hip=-8, right_knee=8, right_ankle=4,
                                 left_shoulder=33, left_elbow=88,
                                 right_shoulder=6, right_elbow=10),
    "walk_back_contact_r": pose(IDLE_GUARD, world_lean=-3,
                                 right_hip=-15, right_knee=5,  right_ankle=5,
                                 left_hip=15,   left_knee=20, left_ankle=-8,
                                 left_shoulder=38, left_elbow=88,
                                 right_shoulder=25, right_elbow=20),
    "walk_back_down_r":    pose(IDLE_GUARD, world_lean=-2,
                                 right_hip=-5, right_knee=12, right_ankle=3,
                                 left_hip=10,  left_knee=15,  left_ankle=-4,
                                 left_shoulder=36, left_elbow=88,
                                 right_shoulder=12, right_elbow=14),
    "walk_back_pass_r":    pose(IDLE_GUARD, world_lean=-1,
                                 right_hip=4,  right_knee=20, right_ankle=-8,
                                 left_hip=3,   left_knee=6,   left_ankle=2,
                                 left_shoulder=34, left_elbow=88,
                                 right_shoulder=5, right_elbow=12),
    "walk_back_up_r":      pose(IDLE_GUARD, world_lean=-2,
                                 right_hip=10,  right_knee=15, right_ankle=-4,
                                 left_hip=-8,  left_knee=8,  left_ankle=4,
                                 left_shoulder=30, left_elbow=88,
                                 right_shoulder=-8, right_elbow=10),

    # VICTORY / TAUNT
   
    "victory_raise_arm": pose(IDLE_GUARD,
                               right_shoulder=-170, right_elbow=12, right_wrist=180,
                               left_shoulder=30, left_elbow=85,
                               torso_rot=-5, world_lean=-2),
    "victory_shield_up": pose(IDLE_GUARD,
                               right_shoulder=-170, right_elbow=12, right_wrist=180,
                               left_shoulder=30, left_elbow=85,
                               torso_rot=-5, world_lean=-2, neck=-8),
    "victory_look_up":   pose(IDLE_GUARD,
                               right_shoulder=-170, right_elbow=12, right_wrist=180,
                               left_shoulder=30, left_elbow=85,
                               neck=-12, torso_rot=-8, world_lean=-4),
    "victory_hold":      pose(IDLE_GUARD,
                               right_shoulder=-170, right_elbow=12, right_wrist=180,
                               left_shoulder=30, left_elbow=85,
                               torso_rot=-8, world_lean=-4),

    
    # READY / RESET and BREATH LOOP
    
    "ready_reset":   pose(IDLE_GUARD, torso_rot=-2, neck=-2),
    "breath_inhale": pose(IDLE_GUARD, torso_rot=-3, neck=-1, world_lean=1),
    "breath_exhale": pose(IDLE_GUARD, torso_rot=2,  neck=1,  world_lean=-1),
}

# Walk forward cycle: 8 keyframes
WALK_CYCLE = [
    "walk_contact_l", "walk_down_l", "walk_pass_l", "walk_up_l",
    "walk_contact_r", "walk_down_r", "walk_pass_r", "walk_up_r",
]

# Walk back cycle: 8 keyframes
WALK_BACK_CYCLE = [
    "walk_back_contact_l", "walk_back_down_l", "walk_back_pass_l", "walk_back_up_l",
    "walk_back_contact_r", "walk_back_down_r", "walk_back_pass_r", "walk_back_up_r",
]

# Run cycle: 8 keyframes
RUN_CYCLE = [
    "run_contact_l", "run_down_l", "run_pass_l", "run_flight_l",
    "run_contact_r", "run_down_r", "run_pass_r", "run_flight_r",
]
