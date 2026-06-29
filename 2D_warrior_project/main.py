import sys
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

from character import WarriorRig
import animation
import renderer
from keyframes import POSES
from utils import lerp_pose
from graphics_pipeline import ViewportManager, Camera, AffineTransform

LOGICAL_WIDTH, LOGICAL_HEIGHT = 1060, 560  # extra 200px for side panel
INITIAL_WIN_W, INITIAL_WIN_H = 1280, 720
FPS = 60
RESIZE_HANDLE_W = 24
RESIZE_HANDLE_H = 24


def create_gl_window(size):
    """Create a resizable OpenGL window and return the display surface."""
    return pygame.display.set_mode(
        size,
        pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE,
    )


def is_over_resize_handle(screen_pos, viewport):
    """Return True when the pointer is over the visible resize handle."""
    if screen_pos is None:
        return False

    mouse_x, mouse_y = screen_pos
    if mouse_x < viewport.dx or mouse_x > viewport.dx + viewport.draw_w:
        return False
    if mouse_y < viewport.dy or mouse_y > viewport.dy + viewport.draw_h:
        return False

    logical_x = (mouse_x - viewport.dx) * (LOGICAL_WIDTH / max(1, viewport.draw_w))
    logical_y = (mouse_y - viewport.dy) * (LOGICAL_HEIGHT / max(1, viewport.draw_h))
    handle_x = LOGICAL_WIDTH - 36
    handle_y = LOGICAL_HEIGHT - 36
    return (
        handle_x <= logical_x <= handle_x + RESIZE_HANDLE_W
        and handle_y <= logical_y <= handle_y + RESIZE_HANDLE_H
    )


def draw_resize_handle(surface):
    """Draw a visible resize handle in the bottom-right corner of the scene."""
    x = LOGICAL_WIDTH - 36
    y = LOGICAL_HEIGHT - 36
    rect = pygame.Rect(x, y, RESIZE_HANDLE_W, RESIZE_HANDLE_H)
    pygame.draw.rect(surface, (40, 40, 40), rect)
    pygame.draw.rect(surface, (220, 220, 220), rect, 1)
    pygame.draw.line(surface, (220, 220, 220), (x + 6, y + 18), (x + 18, y + 6), 2)
    pygame.draw.line(surface, (220, 220, 220), (x + 10, y + 18), (x + 18, y + 10), 2)


def main():
    pygame.init()

    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
    screen = create_gl_window((INITIAL_WIN_W, INITIAL_WIN_H))
    pygame.display.set_caption("Ethiopian Warrior - 2D Hierarchical Keyframe Animation")
    clock = pygame.time.Clock()

    offscreen = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    font = pygame.font.SysFont("consolas", 18, bold=True)
    small_font = pygame.font.SysFont("consolas", 14)

    rig = WarriorRig()
    viewport = ViewportManager(LOGICAL_WIDTH, LOGICAL_HEIGHT)
    camera = Camera()
    affine = AffineTransform()

    t = 0.0
    paused = False
    debug_on = False
    showcase_on = False
    showcase_step = 0
    showcase_timer = 0.0
    resize_dragging = False
    resize_start_mouse = None
    resize_start_size = None

    tex_id = glGenTextures(1)
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)
    viewport.on_resize(INITIAL_WIN_W, INITIAL_WIN_H)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Recreate the GL surface and recalculate the viewport for the new aspect ratio.
                win_w = max(1, int(event.w))
                win_h = max(1, int(event.h))
                screen = create_gl_window((win_w, win_h))
                viewport.on_resize(win_w, win_h)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if is_over_resize_handle(event.pos, viewport):
                        resize_dragging = True
                        resize_start_mouse = event.pos
                        resize_start_size = screen.get_size()
                    else:
                        camera.on_mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if resize_dragging:
                        resize_dragging = False
                        resize_start_mouse = None
                        resize_start_size = None
                    else:
                        camera.on_mouse_up()
            elif event.type == pygame.MOUSEMOTION:
                if resize_dragging and resize_start_mouse is not None and resize_start_size is not None:
                    dx = event.pos[0] - resize_start_mouse[0]
                    dy = event.pos[1] - resize_start_mouse[1]
                    new_w = max(640, int(resize_start_size[0] + dx))
                    new_h = max(480, int(resize_start_size[1] + dy))
                    if (new_w, new_h) != screen.get_size():
                        screen = create_gl_window((new_w, new_h))
                        viewport.on_resize(new_w, new_h)
                else:
                    camera.on_mouse_motion(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    debug_on = not debug_on
                elif event.key == pygame.K_s:
                    showcase_on = not showcase_on
                    showcase_step = 0
                    showcase_timer = 0.0
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    t = 0.0
                elif event.key == pygame.K_v:
                    viewport.toggle_projection()

        keys = pygame.key.get_pressed()

        # Camera pan (arrow keys) and zoom (+/-)
        if keys[pygame.K_LEFT]:
            camera.pan(400 * dt, 0)
        if keys[pygame.K_RIGHT]:
            camera.pan(-400 * dt, 0)
        if keys[pygame.K_UP]:
            camera.pan(0, -400 * dt)
        if keys[pygame.K_DOWN]:
            camera.pan(0, 400 * dt)
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:
            camera.zoom_by(1.0, dt)
        if keys[pygame.K_MINUS]:
            camera.zoom_by(-1.0, dt)

        # Warrior affine transforms (accumulated state, applied once per frame)
        affine.update_from_keys(keys, pygame, dt)

        if not paused:
            t += dt
            if t > animation.TOTAL_DURATION:
                t = 0.0

        if showcase_on:
            showcase_timer += dt
            if showcase_timer >= renderer.SHOWCASE_STEP_TIME:
                showcase_timer = 0.0
                showcase_step = (showcase_step + 1) % len(renderer.SHOWCASE_STEPS)

        if showcase_on and showcase_step == 3:
            frac = (showcase_timer / renderer.SHOWCASE_STEP_TIME) % 1.0
            pose = lerp_pose(POSES["idle_guard"], POSES.get("spear_thrust", POSES["atk_thrust_ext"]), frac)
            root_x, root_y = 0.0, 0.0
            breathe_scale, head_turn, blink, back_view, scale_x = 1.0, 0.0, False, False, 1.0  # force face-right
        else:
            pose, root_x, root_y, breathe_scale, head_turn, blink, back_view, scale_x = animation.evaluate(t)

        base_x = 200
        base_y = renderer.GROUND_Y - 55

        rig.apply_pose(
            pose, base_x + root_x, base_y + root_y,
            breathe_scale=breathe_scale,
            head_turn=head_turn,
            blink=blink,
            back_view=back_view,
            scale_x=scale_x,
        )
        rig.apply_manual_affine(
            affine.tx, affine.ty, affine.rotation, affine.scale, scale_x=scale_x,
        )

        renderer.draw_background(offscreen, LOGICAL_WIDTH, LOGICAL_HEIGHT)
        rig.draw(offscreen)

        if debug_on:
            renderer.draw_debug_skeleton(offscreen, small_font, rig.world)

        renderer.draw_hud(
            offscreen, font, small_font, t,
            animation.get_scene_name(t), debug_on, showcase_on,
            projection_mode=viewport.mode_label,
            cam_zoom=camera.zoom,
            obj_scale=affine.scale,
        )
        draw_resize_handle(offscreen)

        if showcase_on:
            renderer.draw_showcase_overlay(offscreen, font, small_font, showcase_step, showcase_timer)

        data = pygame.image.tostring(offscreen, "RGBA", True)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, LOGICAL_WIDTH, LOGICAL_HEIGHT,
            0, GL_RGBA, GL_UNSIGNED_BYTE, data,
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        viewport.apply_projection()

        glPushMatrix()
        camera.apply_modelview(LOGICAL_WIDTH, LOGICAL_HEIGHT, viewport.is_perspective)

        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0); glVertex2f(0.0, 0.0)
        glTexCoord2f(1.0, 0.0); glVertex2f(LOGICAL_WIDTH, 0.0)
        glTexCoord2f(1.0, 1.0); glVertex2f(LOGICAL_WIDTH, LOGICAL_HEIGHT)
        glTexCoord2f(0.0, 1.0); glVertex2f(0.0, LOGICAL_HEIGHT)
        glEnd()

        glPopMatrix()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
