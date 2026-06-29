import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "Desktop", "cc", "ethiopian_warrior_animation", "warrior_project")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "warrior_project")))
sys.path.append(os.path.abspath("warrior_project"))

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from character import WarriorRig
import animation
import renderer

WIDTH, HEIGHT = 860, 560
# Peak timestamps for each pose
TIMESTAMPS = [0.0, 25.0, 40.0, 62.5, 84.0, 109.5, 120.0]
OUTPUT_DIR = os.path.abspath(os.path.dirname(__file__))

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    font = pygame.font.SysFont("consolas", 18, bold=True)
    small_font = pygame.font.SysFont("consolas", 14)
    
    rig = WarriorRig()
    
    for t in TIMESTAMPS:
        pose, root_x, root_y, breathe_scale, head_turn, blink = animation.evaluate(t)
        base_x, base_y = 220, renderer.GROUND_Y - 60
        
        # Apply pose
        rig.apply_pose(pose, base_x + root_x, base_y + root_y,
                       breathe_scale=breathe_scale, head_turn=head_turn, blink=blink)
        
        # Draw frame
        renderer.draw_background(screen, WIDTH, HEIGHT)
        rig.draw(screen)
        renderer.draw_hud(screen, font, small_font, t, animation.get_scene_name(t), False, False)
        
        # Save screenshot using float timestamp in filename so it's precise
        filename = os.path.join(OUTPUT_DIR, f"pose_{t}s.png")
        pygame.image.save(screen, filename)
        print(f"Saved {filename}")

if __name__ == "__main__":
    main()
