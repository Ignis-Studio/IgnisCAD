import build123d as bd
import webbrowser

from igniscad._err_handler import wrap_handlers

_GLOBAL_LAST_PART = None
wrap_handlers()

class ContextManager:
    """
    A context manager to capture generated models(Entity objects).
    """

    def __init__(self, name):
        self.name = name
        self.part = None
        self.registry = {}

    # Context manager for *with* statements.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cache the current part in _GLOBAL_LAST_PART
        # which is used by show()
        global _GLOBAL_LAST_PART
        if self.part:
            self.part.label = self.name  # names as labels
            _GLOBAL_LAST_PART = self.part
        return

    # Operator overriding
    def __lshift__(self, other):
        """
        Override the "<<" operator
        Usage: item << Cylinder(...) - Box(...)
        """
        if isinstance(other, Entity):
            self.part = self.part + other if self.part else other
            if other.name:
                self.registry[other.name] = other
        return self

    # Registry utils

    # Note: advantages of using a registry:
    # being *disvariabled*
    # you can define an entity without wrapping them into a variable
    # variables are easy to be ripped off between different contexts
    # you can call this entity anywhere through item.f(<entity.name_in_registry>)
    # you can also edit the registry by yourself, but that's not recommended.
    def find(self, name: str):
        """
        To find an Entity by its name in the registry.
        Args:
            name (str): Entity name
        """
        if name in self.registry:
            return self.registry[name]
        raise ValueError(f"❌ Part '{name}' not found in this item.")

    def f(self, name: str):
        return self.find(name)


class Entity:
    """
    A base class for every wrapped build123d objects.
    The original build123d objects can be called with entity.part .
    """
    def __init__(self, part: bd.Part | None, name=None):
        self.part = part
        self.name = name

    # Transition logic
    def move(self, x=0, y=0, z=0):
        return Entity(self.part.moved(bd.Location((x, y, z))), self.name)

    def rotate(self, x=0, y=0, z=0):
        p = self.part
        if x: p = p.rotate(bd.Axis.X, x)
        if y: p = p.rotate(bd.Axis.Y, y)
        if z: p = p.rotate(bd.Axis.Z, z)
        return Entity(p, self.name)

    # Set-like operations
    def _wrap_result(self, res):
        """
        Inner helper function to wrap the result into a *single* build123d object.
        The *show()* function require a single Compound or Solid object to save the .stl file.
        """
        if not isinstance(res, (bd.Compound, bd.Solid)):
            res = bd.Compound(res)
        return res

    def __sub__(self, other):
        return self._wrap_result(self.part - other.part)

    def __add__(self, other):
        return self._wrap_result(self.part + other.part)

    def __and__(self, other):
        return self._wrap_result(self.part & other.part)

    # Syntactic properties
    @property
    def bbox(self):
        """Grabbing the bounding box of the entity."""
        return self.part.bounding_box()

    @property
    def top(self):
        """Grabbing the Z pos of the center point of the top surface of the entity."""
        return self.bbox.max.Z

    @property
    def right(self):
        """Grabbing the maximum X pos."""
        return self.bbox.max.X

    @property
    def radius(self):
        """Estimate the radius of the entity(only for spheres and/or cylinders)."""
        # Simple logic: Grabbing half the width in the X direction.
        return self.bbox.size.X / 2

    # Universal alignment (syntactic)
    def align(self, target, face="top", offset=0):
        """
        *Snap* the current Entity to a specified face of the target.

        Calculation:
            Center pos of the target surface + Half of the current's thickness + Additional gap

        Args:
            target (Entity): The target Entity
            face (str): "top", "bottom", "left", "right", "front", "back"
            offset (float): Addition gap between the current and the target.
                (A positive number refers to a gap and a negative number refers to an embedding.)
        """
        if not isinstance(target, Entity):
            raise ValueError("Target must be an Entity")

        # Grabbing the bounding box.
        t_box = target.bbox  # Target Bounding Box
        s_box = self.bbox  # Self Bounding Box (Current)

        # The default goal pos is target.center().
        dest_x = t_box.center().X
        dest_y = t_box.center().Y
        dest_z = t_box.center().Z

        # Own size (Width, Depth, Height)
        s_w = s_box.size.X
        s_d = s_box.size.Y
        s_h = s_box.size.Z

        # Adjust the goal pos according to the *face* argument.
        # Calculation:
        # Center pos of the target surface +/- Half of the current's thickness +/- Additional gap
        f = face.lower()

        # Z direction
        if f == "top":
            dest_z = t_box.max.Z + (s_h / 2) + offset
        elif f == "bottom":
            dest_z = t_box.min.Z - (s_h / 2) - offset

        # X direction
        elif f == "right":
            dest_x = t_box.max.X + (s_w / 2) + offset
        elif f == "left":
            dest_x = t_box.min.X - (s_w / 2) - offset

        # Y direction
        elif f == "back":
            dest_y = t_box.max.Y + (s_d / 2) + offset
        elif f == "front":
            dest_y = t_box.min.Y - (s_d / 2) - offset
        else:
            raise ValueError(f"❌ Unknown face: {face}. Use top/bottom/left/right/front/back")

        # Calculate the displacement vector (target.center() - current.center())
        # Necessary!
        curr_x = s_box.center().X
        curr_y = s_box.center().Y
        curr_z = s_box.center().Z

        dx = dest_x - curr_x
        dy = dest_y - curr_y
        dz = dest_z - curr_z

        return self.move(dx, dy, dz)

    # Syntactic Sugar for AI agents

    def on_top_of(self, target, offset=0):
        return self.align(target, "top", offset)

    def under(self, target, offset=0):
        return self.align(target, "bottom", offset)

    def right_of(self, target, offset=0):
        return self.align(target, "right", offset)

    def left_of(self, target, offset=0):
        return self.align(target, "left", offset)

    def in_front_of(self, target, offset=0):
        return self.align(target, "front", offset)

    def behind(self, target, offset=0):
        return self.align(target, "back", offset)


# Top level APIs

def Item(name: str) -> ContextManager:
    """
    Factory function for creating a context.
    Can only be used once in a single model.
    """
    return ContextManager(name)


def show():
    """
    Try connecting Yet Another CAD Viewer (within the browser)，
    If failed: fallback to save and open the *.stl file.
    """
    global _GLOBAL_LAST_PART
    if not _GLOBAL_LAST_PART:
        print("⚠️ Nothing to show! (Did you forget to use 'item << ...'?)")
        return

    label = _GLOBAL_LAST_PART.label or "Model"
    print(f"👀 Processing: {label}")

    # Try connecting Yet Another CAD Viewer (YACV)
    try:
        from yacv_server import show as yacv_show
        target_obj = _GLOBAL_LAST_PART
        yacv_show(target_obj, names=[label])

        url = "http://localhost:32323"
        print(f"✅ Sent to YACV (Check your browser, at {url})")
        webbrowser.open(url)
        input("✅ Press Enter to exit...")
        return
    except Exception as e:
        print(f"⚠️ Failed to connect to YACV: {e}")

    # If failed: fallback to save and open the *.stl file.
    print("⚠️ Viewer not available. Exporting to disk...")
    filename = f"{label}.stl"

    try:
        bd.export_stl(_GLOBAL_LAST_PART, filename)
    except NameError:
        import build123d as bd_fallback
        bd_fallback.export_stl(_GLOBAL_LAST_PART, filename)

    import os
    abs_path = os.path.abspath(filename)
    print(f"💾 Saved: {abs_path}")
    print("👉 You can open this file with Windows 3D Viewer.")

    try:
        os.startfile(abs_path)
    except:
        pass

# Primitives for AI agents.
# Note: center aligning is defaulted.

def Box(x, y, z, name=None) -> Entity:
    """
    Wrapped function for build123d.Box
    Args:
        x: X coordinate
        y: Y coordinate
        z: Z coordinate
        name: name of the Entity in context registry
    """
    return Entity(bd.Part(bd.Box(x, y, z, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))), name)

def Cylinder(r, h, name=None) -> Entity:
    """
    Wrapped function for build123d.Cylinder
    Args:
        r: radius
        h: height
        name: name of the Entity in context registry
    """
    return Entity(bd.Part(bd.Cylinder(radius=r, height=h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))), name)

def Sphere(r, name=None) -> Entity:
    """
    Wrapped function for build123d.Sphere
    Args:
        r: radius
        name: name of the Entity in context registry
    """
    return Entity(bd.Part(bd.Sphere(radius=r)), name)

def Torus(major, minor, name=None) -> Entity:
    """
    Wrapped function for build123d.Torus
    Args:
        major: major radius
        minor: minor radius
        name: name of the Entity in context registry
    """
    return Entity(bd.Part(bd.Torus(major_radius=major, minor_radius=minor)), name)


class Group(Entity):
    """
    Combine multiple entities into a single Group Entity.
    Support the same context-manager syntax (as Item does).
    Entities within a group are automatically unioned.
    The Group object can be moved or aligned like a normal Entity outside the *with* statements.
    """

    def __init__(self, name=None):
        """
        Args:
            name: name of the Group in context registry
        """
        super().__init__(part=None, name=name)

    # Context manager for *with* statements.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def __lshift__(self, other):
        """
        Override the "<<" operator
        Usage: group << Entity(...)

        Every entity added is unioned automatically.
        """
        if isinstance(other, Entity):
            if self.part is None:
                # Initialize a new group with the current part as a basement.
                self.part = other.part
            else:
                # Union the new part with the old parts.
                self.part = self.part + other.part
        else:
            raise ValueError("❌ Group implies adding Entity objects (Box, Cylinder, etc.)")

        return self
