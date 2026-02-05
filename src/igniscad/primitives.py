"""
Primitives for AI agents.
Note: center aligning is defaulted.
"""

from igniscad.core import Entity
import build123d as bd


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


