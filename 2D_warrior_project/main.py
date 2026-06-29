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


def main():
    pygame.init()

    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
    screen = pygame.display.set_mode(
        (INITIAL_WIN_W, INITIAL_WIN_H),
        pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE,
    )
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
                # Recreate GL surface and update viewport + projection for new aspect ratio
                screen = pygame.display.set_mode(
                    (event.w, event.h),
                    pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE,
                )
                viewport.on_resize(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    camera.on_mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    camera.on_mouse_up()
            elif event.type == pygame.MOUSEMOTION:
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
