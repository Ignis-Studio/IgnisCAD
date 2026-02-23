"""
This module provides a set of classes that wrap lists of build123d objects (like
Faces, Edges, or Vertices) and expose a fluent API for filtering, sorting, and
modifying them. This allows for expressive, chainable commands.

Example:
    box = Box(10, 10, 10)
    # Select the top face of the box and apply a fillet to its edges.
    filleted_box = box.faces().top().fillet(2)
"""

from __future__ import annotations
from typing import Callable, Iterable, Union, Generic, TypeVar, TYPE_CHECKING
import build123d as bd
from enum import Enum

from build123d import Face

if TYPE_CHECKING:
    from igniscad.core import Entity

T = TypeVar("T", bd.Face, bd.Edge, bd.Vertex, bd.Solid, bd.Shell, bd.Wire, bd.Compound)

class Axis(Enum):
    """An enumeration for the three Cartesian axes (X, Y, Z)."""
    X = "X"
    Y = "Y"
    Z = "Z"

class Selector(Generic[T]):
    """A generic selector for lists of build123d objects.

    The Selector class is the foundation of the fluent selection API. It holds a
    list of geometric items and a reference to a parent Entity, allowing for
    chainable operations and modifications that affect the original model.

    Attributes:
        _items (list[T]): The list of geometric objects this selector holds.
        parent (Entity | None): A reference to the parent Entity from which the
            items were selected. This is necessary for applying modifications.
    """

    def __init__(self, items: Iterable[T], parent: "Entity" = None):
        """Initializes a Selector.

        Args:
            items (Iterable[T]): A collection of geometric objects to be wrapped.
            parent (Entity, optional): The parent entity. Defaults to None.
        """
        self._items = list(items)
        self.parent = parent

    def __iter__(self):
        """Returns an iterator over the selected items."""
        return iter(self._items)

    def __len__(self):
        """Returns the number of items in the selector."""
        return len(self._items)

    def __getitem__(self, key):
        """Retrieves an item by index."""
        return self._items[key]

    @property
    def first(self) -> T | None:
        """Returns the first item in the selection, or None if empty."""
        return self._items[0] if self._items else None

    @property
    def last(self) -> T | None:
        """Returns the last item in the selection, or None if empty."""
        return self._items[-1] if self._items else None

    def get(self) -> list[T]:
        """Returns the raw list of selected items."""
        return self._items
        
    def tag(self, tag_name: str) -> "Selector[T]":
        """Assigns a tag to all items in the current selection.

        This method adds the selected items to the parent Entity's tag dictionary,
        allowing them to be easily retrieved later using `get_by_tag()`.

        Args:
            tag_name (str): The name of the tag to assign.

        Returns:
            Selector[T]: The same selector instance, for chainability.

        Raises:
            ValueError: If the selector does not have a parent entity.
        """
        if not self.parent:
            raise ValueError("Cannot tag items without a parent entity.")
        
        for item in self._items:
            self.parent.tags[tag_name].append(item)
        
        return self

    def filter_by(self, criteria: Union[Callable[[T], bool], Axis]) -> "Selector[T]":
        """Filters the selection based on a given criteria.

        Args:
            criteria (Union[Callable[[T], bool], Axis]): A predicate function
                that returns True for items to keep, or an Axis to filter items
                in the positive direction of that axis.

        Returns:
            Selector[T]: A new selector containing only the filtered items.
        
        Raises:
            TypeError: If the criteria is not a callable or an Axis.
        """
        if isinstance(criteria, Axis):
            axis = criteria
            def filter_func(item: T):
                com = item.center()
                if axis == Axis.X:
                    return com.X > 0
                elif axis == Axis.Y:
                    return com.Y > 0
                else: # Z
                    return com.Z > 0
            filtered_items = filter(filter_func, self._items)
        elif callable(criteria):
            filtered_items = filter(criteria, self._items)
        else:
            raise TypeError("Criteria must be a callable or an Axis enum.")
        
        return self.__class__(filtered_items, self.parent)

    def sort_by(self, sort_key: Union[str, Callable[[T], float]], reverse: bool = False) -> "Selector[T]":
        """Sorts the selection.

        Args:
            sort_key (Union[str, Callable[[T], float]]): The key to sort by.
                Can be a callable that returns a numeric value, or a string
                ('X', 'Y', 'Z') to sort by the center coordinate.
            reverse (bool, optional): If True, sorts in descending order.
                Defaults to False.

        Returns:
            Selector[T]: A new selector with the sorted items.
        
        Raises:
            TypeError: If the sort_key is not a callable or a valid axis string.
        """
        if isinstance(sort_key, str) and sort_key in ["X", "Y", "Z"]:
            def key_func(item: T):
                return getattr(item.center(), sort_key)
            sorted_items = sorted(self._items, key=key_func, reverse=reverse)
        elif callable(sort_key):
            sorted_items = sorted(self._items, key=sort_key, reverse=reverse)
        else:
            raise TypeError("sort_key must be a callable or one of 'X', 'Y', 'Z'.")
        
        return self.__class__(sorted_items, self.parent)

class FaceSelector(Selector[bd.Face]):
    """A selector specialized for handling `build123d.Face` objects."""

    def top(self) -> "FaceSelector":
        """Selects the face with the highest Z-coordinate center.

        Returns:
            FaceSelector: A new selector containing only the top-most face.
        """
        if not self._items:
            return self.__class__([], self.parent)
        top_face = max(self._items, key=lambda f: f.center().Z)
        return self.__class__([top_face], self.parent)

    def bottom(self) -> "FaceSelector":
        """Selects the face with the lowest Z-coordinate center.

        Returns:
            FaceSelector: A new selector containing only the bottom-most face.
        """
        if not self._items:
            return self.__class__([], self.parent)
        bottom_face = min(self._items, key=lambda f: f.center().Z)
        return self.__class__([bottom_face], self.parent)

    def sort_by_area(self, reverse: bool = False) -> Selector[Face]:
        """Sorts the faces by their surface area.

        Args:
            reverse (bool, optional): If True, sorts from largest to smallest.
                Defaults to False.

        Returns:
            FaceSelector: A new selector with the faces sorted by area.
        """
        return self.sort_by(sort_key=lambda f: f.area, reverse=reverse)

    def face_intersecting(self, other: Entity, tolerance: float = 1e-5) -> "FaceSelector":
        """
        Selects faces that physically overlap with a given shape (Area > 0).

        Uses a boolean intersection to determine if the face shares a common
        surface area with the target object. This excludes faces that only
        touch at edges or corners.

        Args:
            other (Entity): The reference Entity to check against.
            tolerance (float, optional): Minimum area to be considered intersecting.
                Also used for the preliminary distance check. Defaults to 1e-5.

        Returns:
            FaceSelector: A new selector containing only the mating/overlapping faces.
        """
        if not self._items:
            return self.__class__([], self.parent)

        touching_faces = []
        for face in self._items:
            if face.distance_to(other.part) > tolerance:
                continue

            intersection = face & other.part
            if intersection and intersection.area > tolerance:
                touching_faces.append(face)

        return self.__class__(touching_faces, self.parent)

    def fillet(self, radius: float) -> "Entity":
        """Applies a fillet to all edges of the selected faces.

        Args:
            radius (float): The fillet radius.

        Returns:
            Entity: A new Entity object with the modification applied.
        """
        if not self.parent:
            raise ValueError("Cannot perform modification without a parent entity.")
        
        edges_to_fillet = []
        for face in self._items:
            edges_to_fillet.extend(face.edges())
        
        return self.parent.fillet(radius, edges=edges_to_fillet)

    def chamfer(self, distance: float) -> "Entity":
        """Applies a chamfer to all edges of the selected faces.

        Args:
            distance (float): The chamfer distance.

        Returns:
            Entity: A new Entity object with the modification applied.
        """
        if not self.parent:
            raise ValueError("Cannot perform modification without a parent entity.")
        
        edges_to_chamfer = []
        for face in self._items:
            edges_to_chamfer.extend(face.edges())
            
        return self.parent.chamfer(distance, edges=edges_to_chamfer)

class EdgeSelector(Selector[bd.Edge]):
    """A selector specialized for handling `build123d.Edge` objects."""

    def closest_to(self, point: bd.Vector) -> "EdgeSelector":
        """Selects the edge closest to a given point.

        Args:
            point (bd.Vector): The reference point.

        Returns:
            EdgeSelector: A new selector containing only the closest edge.
        """
        if not self._items:
            return self.__class__([], self.parent)
        closest_edge = min(self._items, key=lambda e: e.dist_to_point(point))
        return self.__class__([closest_edge], self.parent)

    def fillet(self, radius: float) -> "Entity":
        """Applies a fillet to the selected edges.

        Args:
            radius (float): The fillet radius.

        Returns:
            Entity: A new Entity object with the modification applied.
        """
        if not self.parent:
            raise ValueError("Cannot perform modification without a parent entity.")
        return self.parent.fillet(radius, edges=self._items)

    def chamfer(self, distance: float) -> "Entity":
        """Applies a chamfer to the selected edges.

        Args:
            distance (float): The chamfer distance.

        Returns:
            Entity: A new Entity object with the modification applied.
        """
        if not self.parent:
            raise ValueError("Cannot perform modification without a parent entity.")
        return self.parent.chamfer(distance, edges=self._items)

class VertexSelector(Selector[bd.Vertex]):
    """A selector specialized for handling `build123d.Vertex` objects."""



    def closest_to(self, point: bd.Vector) -> "VertexSelector":
        """Selects the vertex closest to a given point.

        Args:
            point (bd.Vector): The reference point.

        Returns:
            VertexSelector: A new selector containing only the closest vertex.
        """
        if not self._items:
            return self.__class__([], self.parent)
        closest_vertex = min(self._items, key=lambda v: v.center().distance_to(point))
        return self.__class__([closest_vertex], self.parent)

class SolidSelector(Selector[bd.Solid]):
    """A selector specialized for handling `build123d.Solid` objects.
    
    This selector only provides the generic functionality inherited
    from the base Selector class.
    """
    pass
