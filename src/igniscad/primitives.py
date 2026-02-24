"""
Primitives for AI agents.
Note: center aligning is defaulted for all primitives.
"""

import math
from igniscad.core import Entity
from igniscad.helpers.validator import validate_dimensions
import build123d as bd


@validate_dimensions("x", "y", "z")
def Box(x: float, y: float, z: float, name: str = None) -> Entity:
    """
    Wrapped function for build123d.Box.

    Args:
        x (float): X coordinate
        y (float): Y coordinate
        z (float): Z coordinate
        name (str): name of the Entity in context registry
    """
    return Entity(bd.Box(x, y, z, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)), name)


@validate_dimensions("r", "h")
def Cylinder(r: float, h: float, name: str = None) -> Entity:
    """
    Wrapped function for build123d.Cylinder.

    Args:
        r (float): radius
        h (float): height
        name (str): name of the Entity in context registry
    """
    return Entity(bd.Cylinder(radius=r, height=h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)), name)


@validate_dimensions("r")
def Sphere(r: float, name: str = None) -> Entity:
    """
    Wrapped function for build123d.Sphere.

    Args:
        r (float): radius
        name (str): name of the Entity in context registry
    """
    return Entity(bd.Sphere(radius=r), name)


@validate_dimensions("major", "minor")
def Torus(major: float, minor: float, name: str = None) -> Entity:
    """
    Wrapped function for build123d.Torus.

    Args:
        major (float): major radius
        minor (float): minor radius
        name (str): name of the Entity in context registry
    """
    return Entity(bd.Torus(major_radius=major, minor_radius=minor), name)


@validate_dimensions("bottom_radius", "top_radius", "h")
def Cone(bottom_radius: float, top_radius: float, h: float, name: str = None) -> Entity:
    """
    Wrapped function for build123d.Cone.

    Args:
        bottom_radius (float): bottom radius
        top_radius (float): top radius
        h (float): height
        name (str): name of the Entity in context registry
    """
    return Entity(bd.Cone(bottom_radius=bottom_radius, top_radius=top_radius, height=h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)), name)


@validate_dimensions("xsize", "ysize", "zsize", "xmax", "xmin", "ymax", "ymin")
def Wedge(xsize: float, ysize: float, zsize: float, xmax: float, xmin: float, ymax: float, ymin: float,
          name: str = None) -> Entity:
    """
    Wrapped function for build123d.Wedge.

    Args:
        xsize (float): Base width (X)
        ysize (float): Base depth (Y)
        zsize (float): Height (Z)
        xmax (float): X coordinate of the top face end (relative to origin 0)
        xmin (float): X coordinate of the top face start (relative to origin 0)
        ymax (float): Y coordinate of the top face end (mapped to build123d zmax)
        ymin (float): Y coordinate of the top face start (mapped to build123d zmin)
        name (str): name of the Entity in context registry

    Note:
        In build123d, the *zmax* and *zmin* params control the Y direction, which can be confusing.
        They are re-mapped to *ymax* and *ymin* here for clarity.
    """
    return Entity(bd.Wedge(xsize=xsize, ysize=ysize, zsize=zsize, xmax=xmax, xmin=xmin, zmax=ymax, zmin=ymin), name)


@validate_dimensions("w", "h", "d")
def Slot(w: float, h: float, d: float, name: str = None) -> Entity:
    """
    Wrapped function for a 3D slot.

    Args:
        w (float): slot width on the 2D sketch plane
        h (float): slot height on the 2D sketch plane(diameter)
        d (float): slot depth (extrusion amount)
        name (str): name of the Entity in context registry
    """
    slot_sketch = bd.Sketch(bd.SlotOverall(width=w, height=h / 2))
    # Extrude in both directions from the sketch plane to center the part
    part = bd.extrude(slot_sketch, amount=d / 2, both=True)

    return Entity(part, name)


@validate_dimensions("radius", "cb_radius", "cb_depth", "height")
def CounterBoreHole(radius: float, cb_radius: float, cb_depth: float, height: float, name: str = None) -> Entity:
    """
    Creates a counter-bore hole shape (for boolean subtraction).
    AI description: A hole for a socket head cap screw.

    Args:
        radius (float): Through-hole radius (for the screw shaft)
        cb_radius (float): Counter-bore radius (for the screw head)
        cb_depth (float): Counter-bore depth
        height (float): Total height of the hole
        name (str): Name of the Entity in the context registry
    """
    # 1. Create the main through-hole shaft and convert to Part
    shaft_part = bd.Part(bd.Cylinder(radius=radius, height=height, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)))

    # 2. Create the counter-bore head and convert to Part
    head_part = bd.Part(bd.Cylinder(radius=cb_radius, height=cb_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)))

    # 3. Move the head part to align with the top of the shaft
    head_offset = (height / 2) - (cb_depth / 2)
    head_moved_part = head_part.locate(bd.Location(bd.Vector(0, 0, head_offset)))

    # 4. Combine the parts
    combined_part = shaft_part + head_moved_part

    return Entity(combined_part, name)


@validate_dimensions("radius", "csk_radius", "csk_angle", "height")
def CountersinkHole(radius: float, csk_radius: float, csk_angle: float, height: float, name: str = None) -> Entity:
    """
    Creates a countersink hole shape (for boolean subtraction).
    AI description: A hole for a countersunk screw.

    Args:
        radius (float): Through-hole radius
        csk_radius (float): Countersink top radius
        csk_angle (float): Countersink angle in degrees (e.g., 82, 90)
        height (float): Total height of the hole
        name (str): Name of the Entity in the context registry
    """
    # Calculate countersink depth from the angle and radii
    csk_depth = (csk_radius - radius) / math.tan(math.radians(csk_angle / 2))

    # 1. Create the main through-hole shaft and convert to Part
    shaft_part = bd.Part(bd.Cylinder(radius=radius, height=height, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)))

    # 2. Create the countersink head (a cone) and convert to Part
    head_part = bd.Part(bd.Cone(bottom_radius=radius, top_radius=csk_radius, height=csk_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)))

    # 3. Move the head part to align with the top of the shaft
    head_offset = (height / 2) - (csk_depth / 2)
    head_moved_part = head_part.locate(bd.Location(bd.Vector(0, 0, head_offset)))

    # 4. Combine the parts
    combined_part = shaft_part + head_moved_part

    return Entity(combined_part, name)


def ISO_Hole(size: str, depth: float, fit: str = "Normal", name: str = None) -> Entity:
    """
    Creates a standard ISO metric screw clearance hole.

    Args:
        size (str): "M2", "M3", "M4", "M5", "M6", "M8", "M10", "M12"
        depth (float): Depth of the hole
        fit (str): "Close" (tight fit), "Normal" (standard), "Loose" (clearance)
        name (str): Name of the Entity in the context registry
    """
    # ISO 273 clearance hole diameters (in mm)
    specs = {
        "M2": {"Close": 2.2, "Normal": 2.4, "Loose": 2.6},
        "M3": {"Close": 3.2, "Normal": 3.4, "Loose": 3.6},
        "M4": {"Close": 4.3, "Normal": 4.5, "Loose": 4.8},
        "M5": {"Close": 5.3, "Normal": 5.5, "Loose": 5.8},
        "M6": {"Close": 6.4, "Normal": 6.6, "Loose": 7},
        "M8": {"Close": 8.4, "Normal": 9, "Loose": 10},
        "M10": {"Close": 10.5, "Normal": 11, "Loose": 12},
        "M12": {"Close": 13, "Normal": 13.5, "Loose": 14.5},
    }

    size_upper = size.upper()
    if size_upper not in specs:
        raise ValueError(f"Unsupported ISO hole size: {size}. Supported sizes are: {list(specs.keys())}")
    if fit not in specs[size_upper]:
        raise ValueError(f"Unsupported fit: {fit}. Supported fits are: {list(specs[size_upper].keys())}")

    diameter = specs[size_upper][fit]
    radius = diameter / 2

    return Cylinder(r=radius, h=depth, name=name)
