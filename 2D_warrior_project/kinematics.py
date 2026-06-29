from utils import mat_mult, mat_translate, mat_rotate, mat_scale, transform_point


class Joint:
    """One node in the hierarchical character skeleton."""

    def __init__(self, name, offset=(0.0, 0.0), angle=0.0, scale=1.0, draw_fn=None):
        self.name = name
        self.offset = offset      # translation from parent origin to this joint (parent-local)
        self.angle = angle        # local rotation in degrees (the animated DOF)
        self.scale = scale        # local uniform scale (used for breathing, etc.)
        self.draw_fn = draw_fn    # callable(surface, world_matrix, extra) -> None
        self.children = []
        self.world_matrix = None
        self.extra = {}           # auxiliary per-frame draw parameters (blink, gaze, etc.)

    def add(self, *children):
        self.children.extend(children)
        return self

    def find(self, name):
        if self.name == name:
            return self
        for c in self.children:
            found = c.find(name)
            if found:
                return found
        return None

    def update(self, parent_matrix):
        """Recompute this joint's world matrix and propagate to children.
        This is the heart of Forward Kinematics: composing matrices down
        the tree so every descendant inherits every ancestor's transform."""
        local = mat_mult(
            mat_translate(*self.offset),
            mat_mult(mat_rotate(self.angle), mat_scale(self.scale, self.scale)),
        )
        self.world_matrix = mat_mult(parent_matrix, local)
        for c in self.children:
            c.update(self.world_matrix)

    def draw(self, surface):
        if self.draw_fn is not None:
            self.draw_fn(surface, self.world_matrix, self.extra)
        for c in self.children:
            c.draw(surface)

    def origin(self):
        """World-space position of this joint's pivot (for debug skeleton)."""
        return transform_point(self.world_matrix, (0.0, 0.0))

    def walk(self):
        """Yield (joint, parent) for every node - used by the debug renderer."""
        def _walk(node, parent):
            yield node, parent
            for c in node.children:
                yield from _walk(c, node)
        yield from _walk(self, None)


class BodyPart:
    """A small composite-object wrapper: pairs a drawing function with its
    own fixed parameters (color, dimensions, pattern choice...). Several
    BodyPart instances can be owned by a single Joint, which is how the
    Torso joint independently draws an Upper-Torso part AND a Lower-Torso
    part as two distinct drawable objects while still moving as one
    rotating joint in the kinematic hierarchy - a direct demonstration of
    Composite Object Modeling layered on top of the FK skeleton."""

    def __init__(self, draw_func, **kwargs):
        self.draw_func = draw_func
        self.kwargs = kwargs

    def draw(self, surface, matrix, extra=None):
        self.draw_func(surface, matrix, extra or {}, **self.kwargs)
