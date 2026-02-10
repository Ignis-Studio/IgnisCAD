"""
2D Primitives and operations for AI agents.
"""

import build123d as bd
from igniscad.core import Entity

# 2D Primitives

def Rectangle(x: float, y: float, name: str = None) -> Entity:
    """
    Creates a 2D rectangle sketch.

    Args:
        x (float): Width of the rectangle.
        y (float): Height of the rectangle.
        name (str): Name of the Entity in the context registry.
    """
    sketch = bd.Rectangle(x, y)
    return Entity(sketch, name)

def Circle(r: float, name: str = None) -> Entity:
    """
    Creates a 2D circle sketch.

    Args:
        r (float): Radius of the circle.
        name (str): Name of the Entity in the context registry.
    """
    sketch = bd.Circle(r)
    return Entity(sketch, name)

def Polygon(*points, name: str = None) -> Entity:
    """
    Creates a 2D polygon from a list of points.

    Args:
        *points: A list of (x, y) tuples representing the vertices of the polygon.
        name (str): Name of the Entity in the context registry.
    """
    sketch = bd.Polygon(*points)
    return Entity(sketch, name)

def Text(txt: str, font_size: float, font: str = "Arial", name: str = None) -> Entity:
    """
    Creates a 2D text sketch.

    Args:
        txt (str): The text to be rendered.
        font_size (float): The size of the font.
        font (str): The name of the font.
        name (str): Name of the Entity in the context registry.
    """
    sketch = bd.Text(txt, font_size=font_size, font=font)
    return Entity(sketch, name)


# 3D Operations from 2D Sketches

def Extrude(sketch: Entity, amount: float, name: str = None) -> Entity:
    """
    Extrudes a 2D sketch into a 3D part.

    Args:
        sketch (Entity): The 2D sketch entity to extrude.
        amount (float): The extrusion distance.
        name (str): Name of the new 3D Entity.
    """
    if not isinstance(sketch.part, (bd.Sketch, bd.Face)):
        raise TypeError(f"Extrude operation requires a 2D sketch or face, not {type(sketch.part)}.")
    
    part = bd.extrude(sketch.part, amount=amount)
    return Entity(part, name)

def Revolve(sketch: Entity, axis: bd.Axis = bd.Axis.X, name: str = None) -> Entity:
    """
    Revolves a 2D sketch around an axis to create a 3D part.

    Args:
        sketch (Entity): The 2D sketch entity to revolve.
        axis (bd.Axis): The axis of revolution. Defaults to X-axis.
        name (str): Name of the new 3D Entity.
    """
    if not isinstance(sketch.part, (bd.Sketch, bd.Face)):
        raise TypeError("Revolve operation requires a 2D sketch or face.")

    part = bd.revolve(sketch.part, axis=axis)
    return Entity(part, name)

def Sweep(sketch: Entity, path: Entity, name: str = None) -> Entity:
    """
    Sweeps a 2D sketch along a path to create a 3D part.

    Args:
        sketch (Entity): The 2D profile sketch.
        path (Entity): The 1D path (e.g., a Line, Spline, or Wire).
        name (str): Name of the new 3D Entity.
    """
    if not isinstance(sketch.part, (bd.Sketch, bd.Face)):
        raise TypeError("Sweep profile must be a 2D sketch or face.")
    if not isinstance(path.part, (bd.Edge, bd.Wire)):
        raise TypeError("Sweep path must be an Edge or Wire.")

    part = bd.sweep(sketch.part, path=path.part)
    return Entity(part, name)

def Loft(*sketches: Entity, name: str = None) -> Entity:
    """
    Creates a 3D part by lofting through a series of 2D sketches.

    Args:
        *sketches (Entity): A sequence of 2D sketch entities to loft through.
        name (str): Name of the new 3D Entity.
    """
    profiles = []
    for sketch in sketches:
        if not isinstance(sketch.part, (bd.Sketch, bd.Face, bd.Wire)):
            raise TypeError("Loft requires sketches, faces, or wires.")
        profiles.append(sketch.part)

    part = bd.loft(sections=profiles)
    return Entity(part, name)
