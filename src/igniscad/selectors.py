"""
This module contains Selector classes for filtering and selecting geometric objects.
"""

from __future__ import annotations
from typing import Callable, Iterable, Union, Generic, TypeVar, TYPE_CHECKING
import build123d as bd
from enum import Enum

if TYPE_CHECKING:
    from igniscad.core import Entity

T = TypeVar("T", bd.Face, bd.Edge, bd.Vertex, bd.Solid, bd.Shell, bd.Wire, bd.Compound)

class Axis(Enum):
    X = "X"
    Y = "Y"
    Z = "Z"

class Selector(Generic[T]):
    """A generic selector for lists of build123d objects."""

    def __init__(self, items: Iterable[T], parent: "Entity" = None):
        self._items = list(items)
        self.parent = parent

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, key):
        return self._items[key]

    @property
    def first(self) -> T | None:
        return self._items[0] if self._items else None

    @property
    def last(self) -> T | None:
        return self._items[-1] if self._items else None

    def get(self) -> list[T]:
        return self._items
        
    def tag(self, tag_name: str) -> "Selector[T]":
        """
        Tags the selected items in the parent Entity.
        """
        if not self.parent:
            raise ValueError("Cannot tag items without a parent entity.")
        
        for item in self._items:
            self.parent.tags[tag_name].append(item)
        
        return self

    def filter_by(self, criteria: Union[Callable[[T], bool], Axis, str]):
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

    def sort_by(self, sort_key: Union[str, Callable[[T], float]], reverse: bool = False):
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
    """A selector for faces."""

    def top(self):
        if not self._items:
            return self.__class__([], self.parent)
        top_face = max(self._items, key=lambda f: f.center().Z)
        return self.__class__([top_face], self.parent)

    def bottom(self):
        if not self._items:
            return self.__class__([], self.parent)
        bottom_face = min(self._items, key=lambda f: f.center().Z)
        return self.__class__([bottom_face], self.parent)

    def sort_by_area(self, reverse: bool = False):
        return self.sort_by(sort_key=lambda f: f.area, reverse=reverse)

    def fillet(self, radius: float):
        if not self.parent:
            raise ValueError("Cannot perform modification without a parent entity.")
        
        edges_to_fillet = []
        for face in self._items:
            edges_to_fillet.extend(face.edges())
        
        return self.parent.fillet(radius, edges=edges_to_fillet)

    def chamfer(self, distance: float):
        if not self.parent:
            raise ValueError("Cannot perform modification without a parent entity.")
        
        edges_to_chamfer = []
        for face in self._items:
            edges_to_chamfer.extend(face.edges())
            
        return self.parent.chamfer(distance, edges=edges_to_chamfer)

class EdgeSelector(Selector[bd.Edge]):
    """A selector for edges."""

    def closest_to(self, point: bd.Vector):
        if not self._items:
            return self.__class__([], self.parent)
        closest_edge = min(self._items, key=lambda e: e.dist_to_point(point))
        return self.__class__([closest_edge], self.parent)

    def fillet(self, radius: float):
        if not self.parent:
            raise ValueError("Cannot perform modification without a parent entity.")
        return self.parent.fillet(radius, edges=self._items)

    def chamfer(self, distance: float):
        if not self.parent:
            raise ValueError("Cannot perform modification without a parent entity.")
        return self.parent.chamfer(distance, edges=self._items)

class VertexSelector(Selector[bd.Vertex]):
    """A selector for vertices."""

    def closest_to(self, point: bd.Vector):
        if not self._items:
            return self.__class__([], self.parent)
        closest_vertex = min(self._items, key=lambda v: v.center().distance_to(point))
        return self.__class__([closest_vertex], self.parent)

class SolidSelector(Selector[bd.Solid]):
    """A selector for solids."""
    pass
