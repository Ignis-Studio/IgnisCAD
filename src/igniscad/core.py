"""
IgnisCAD is a wrapper for the build123d library, designed for AI agents.
Wrappers:
The class Entity is the base wrapper.
Every wrapper has its original build123d object which can be called with:
    entity.part

Registry:
You can call every named entity in the context like this:
    model.f(<name>)
As there will be only one Model in the context, so the function always gives the original Entity.
"""

import build123d as bd
from igniscad.mixins import AlignmentMixin, ModificationMixin
from typing import Union


class Entity(AlignmentMixin, ModificationMixin):
    """
    A base class for every wrapped build123d objects.
    The original build123d objects can be called with entity.part .
    """
    def __init__(self, part: Union[bd.BasePartObject, bd.BaseSketchObject, bd.Part, bd.Face, bd.Shape] | None, name=None):
        self.part = part
        self.name = name

    # Transition logic
    def move(self, x=0, y=0, z=0):
        """
        Move the entity to a specific position.
        """
        return self.__class__(self.wrap_result(self.part.moved(bd.Location((x, y, z)))), self.name)

    def rotate(self, x=0, y=0, z=0):
        """
        Rotate the entity to a specific angle and position.
        """
        p = self.part
        if x: p = p.rotate(bd.Axis.X, x)
        if y: p = p.rotate(bd.Axis.Y, y)
        if z: p = p.rotate(bd.Axis.Z, z)
        return self.__class__(p, self.name)

    # Set-like operations
    @staticmethod
    def wrap_result(res):
        """
        Inner helper function to wrap the result into a *single* build123d object.
        The *show()* function require a single Compound or Solid object to save the .stl file.
        """
        if not isinstance(res, (bd.Compound, bd.Solid, bd.Shell)):
            res = bd.Compound(res)
        return res

    # Overriding the operators.
    def __sub__(self, other):
        return self.__class__(bd.Part(self.wrap_result(self.part - other.part)))

    def __add__(self, other):
        return self.__class__(bd.Part(self.wrap_result(self.part + other.part)))

    def __and__(self, other):
        return self.__class__(bd.Part(self.wrap_result(self.part & other.part)))

