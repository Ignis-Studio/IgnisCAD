"""
Primitives for AI agents.
Note: center aligning is defaulted.
"""

from igniscad.core import Entity
import build123d as bd


def Box(x: int, y: int, z: int, name: str = None) -> Entity:
    """
    Wrapped function for build123d.Box
    Args:
        x (int): X coordinate
        y (int): Y coordinate
        z (int): Z coordinate
        name (str): name of the Entity in context registry
    """
    return Entity(bd.Part(bd.Box(x, y, z, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))), name)

def Cylinder(r: int, h: int, name: str = None) -> Entity:
    """
    Wrapped function for build123d.Cylinder
    Args:
        r (int): radius
        h (int): height
        name (str): name of the Entity in context registry
    """
    return Entity(bd.Part(bd.Cylinder(radius=r, height=h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))), name)

def Sphere(r: int, name: str = None) -> Entity:
    """
    Wrapped function for build123d.Sphere
    Args:
        r (int): radius
        name (str): name of the Entity in context registry
    """
    return Entity(bd.Part(bd.Sphere(radius=r)), name)

def Torus(major: int, minor: int, name: str = None) -> Entity:
    """
    Wrapped function for build123d.Torus
    Args:
        major (int): major radius
        minor (int): minor radius
        name (str): name of the Entity in context registry
    """
    return Entity(bd.Part(bd.Torus(major_radius=major, minor_radius=minor)), name)


