"""
Graphics pipeline utilities.
Handles viewport, camera, projection,
and object transformations.
"""

import math
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *


# Safe limits — prevent zero/negative scale and runaway camera values

CAM_ZOOM_MIN = 0.2
CAM_ZOOM_MAX = 5.0
OBJ_SCALE_MIN = 0.2
OBJ_SCALE_MAX = 3.0
PERSP_EYE_Z = 650.0
NEAR_PLANE = 1.0
FAR_PLANE = 2000.0
PERSP_FOV = 45.0


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


class ProjectionMode:
  ORTHOGRAPHIC = "orthographic"
  PERSPECTIVE = "perspective"


class ViewportManager:
    """
    Handles glViewport letterboxing and projection matrix setup.
    Recalculates projection whenever the window resizes or mode toggles.
    """

    def __init__(self, logical_w, logical_h):
        self.logical_w = logical_w
        self.logical_h = logical_h
        self.win_w = logical_w
        self.win_h = logical_h
        self.dx = 0
        self.dy = 0
        self.draw_w = logical_w
        self.draw_h = logical_h
        self.mode = ProjectionMode.ORTHOGRAPHIC

    def _has_gl_context(self):
        """Return True when an OpenGL-capable display surface is active."""
        try:
            surface = pygame.display.get_surface()
        except Exception:
            return False
        return surface is not None and bool(surface.get_flags() & pygame.OPENGL)

    def on_resize(self, win_w, win_h):
        """Update viewport rect and projection for a new window size."""
        self.win_w = max(64, int(win_w))
        self.win_h = max(64, int(win_h))

        aspect_logical = self.logical_w / self.logical_h
        aspect_window = self.win_w / self.win_h

        if aspect_window > aspect_logical:
            self.draw_h = self.win_h
            self.draw_w = int(self.win_h * aspect_logical)
            self.dx = (self.win_w - self.draw_w) // 2
            self.dy = 0
        else:
            self.draw_w = self.win_w
            self.draw_h = int(self.win_w / aspect_logical)
            self.dx = 0
            self.dy = (self.win_h - self.draw_h) // 2

        if self._has_gl_context():
            glViewport(self.dx, self.dy, self.draw_w, self.draw_h)
        self.apply_projection()

    def toggle_projection(self):
        """Instant switch between orthographic and perspective (V key)."""
        if self.mode == ProjectionMode.ORTHOGRAPHIC:
            self.mode = ProjectionMode.PERSPECTIVE
        else:
            self.mode = ProjectionMode.ORTHOGRAPHIC
        self.apply_projection()

    def apply_projection(self):
        """Build the projection matrix for the current mode and aspect ratio."""
        if not self._has_gl_context():
            return

        aspect = self.draw_w / max(1, self.draw_h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if self.mode == ProjectionMode.ORTHOGRAPHIC:
            gluOrtho2D(0, self.logical_w, 0, self.logical_h)
        else:
            gluPerspective(PERSP_FOV, aspect, NEAR_PLANE, FAR_PLANE)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    @property
    def mode_label(self):
        return "Perspective" if self.mode == ProjectionMode.PERSPECTIVE else "Orthographic"

    @property
    def is_perspective(self):
        return self.mode == ProjectionMode.PERSPECTIVE


class Camera:
    """Interactive camera: pan (arrows), zoom (+/-), rotate (mouse drag)."""

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.zoom = 1.0
        self.rotation = 0.0
        self._dragging = False
        self._last_mouse = (0, 0)

    def pan(self, dx, dy):
        self.x += dx
        self.y += dy

    def zoom_by(self, delta, dt):
        self.zoom = clamp(self.zoom + delta * dt, CAM_ZOOM_MIN, CAM_ZOOM_MAX)

    def rotate_by(self, degrees):
        self.rotation = (self.rotation + degrees) % 360.0

    def on_mouse_down(self, pos):
        self._dragging = True
        self._last_mouse = pos

    def on_mouse_up(self):
        self._dragging = False

    def on_mouse_motion(self, pos):
        if not self._dragging:
            return
        dx = pos[0] - self._last_mouse[0]
        dy = pos[1] - self._last_mouse[1]
        self._last_mouse = pos
        self.rotate_by(dx * 0.4)

    def apply_modelview(self, logical_w, logical_h, perspective):
        """
        Apply camera transform on the OpenGL modelview stack.
        Order: pull back (persp) -> center -> rotate -> zoom -> pan
        """
        glLoadIdentity()
        if perspective:
            glTranslatef(0.0, 0.0, -PERSP_EYE_Z)
        cx = logical_w * 0.5
        cy = logical_h * 0.5
        glTranslatef(cx, cy, 0.0)
        if abs(self.rotation) > 0.001:
            glRotatef(self.rotation, 0.0, 0.0, 1.0)
        glScalef(self.zoom, self.zoom, 1.0)
        glTranslatef(-cx + self.x, -cy + self.y, 0.0)


class AffineTransform:
    """
    User-driven affine transform on the warrior.
    Translation (IJKL), rotation (U/O), uniform scale (N/M).
    Scale is applied about the character pivot — not the world origin.
    """

    def __init__(self):
        self.tx = 0.0
        self.ty = 0.0
        self.rotation = 0.0
        self.scale = 1.0

    def update_from_keys(self, keys, pygame_mod, dt):
        """Read held keys and update accumulated transform state."""
        if keys[pygame_mod.K_j]:
            self.tx -= 200.0 * dt
        if keys[pygame_mod.K_l]:
            self.tx += 200.0 * dt
        if keys[pygame_mod.K_i]:
            self.ty += 200.0 * dt
        if keys[pygame_mod.K_k]:
            self.ty -= 200.0 * dt
        if keys[pygame_mod.K_u]:
            self.rotation += 90.0 * dt
        if keys[pygame_mod.K_o]:
            self.rotation -= 90.0 * dt
        if keys[pygame_mod.K_n]:
            self.scale -= 0.8 * dt
        if keys[pygame_mod.K_m]:
            self.scale += 0.8 * dt
        self.scale = clamp(self.scale, OBJ_SCALE_MIN, OBJ_SCALE_MAX)
        self.rotation = self.rotation % 360.0
