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
from igniscad.mixins import AlignmentMixin, ModificationMixin, EntitySelectorMixin
from typing import Union
from collections import defaultdict


class Entity(AlignmentMixin, ModificationMixin, EntitySelectorMixin):
    """
    A base class for every wrapped build123d objects.
    The original build123d objects can be called with entity.part .
    """
    def __init__(
        self,
        part: Union[bd.BasePartObject, bd.BaseSketchObject, bd.Part, bd.Face, bd.Shape] | None,
        name=None,
        tags=None,
        joints=None,
    ):
        self.part = part
        self.name = name
        self.tags = defaultdict(list)
        if tags:
            self.tags.update(tags)
        self.joints = dict(joints or {})
        for joint_name, joint in list(self.joints.items()):
            self.joints[joint_name] = joint.__class__(owner=self, location=joint.location, name=joint.name)

    def get_by_tag(self, tag: str):
        """
        Get a selector for objects with a given tag.
        """
        from igniscad.selectors import Selector
        items = self.tags.get(tag, [])
        return Selector(items, parent=self)

    # Transition logic
    def move(self, x=0, y=0, z=0):
        """
        Move the entity to a specific position.
        """
        new_part = self.wrap_result(self.part.moved(bd.Location((x, y, z))))
        return self.__class__(new_part, self.name, self.tags, self.joints)

    def rotate(self, x=0, y=0, z=0):
        """
        Rotate the entity to a specific angle and position.
        """
        p = self.part
        if x: p = p.rotate(bd.Axis.X, x)
        if y: p = p.rotate(bd.Axis.Y, y)
        if z: p = p.rotate(bd.Axis.Z, z)
        return self.__class__(p, self.name, self.tags, self.joints)

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
        return self.__class__(bd.Part(self.wrap_result(self.part - other.part)), self.name, self.tags, self.joints)

    def __add__(self, other):
        return self.__class__(bd.Part(self.wrap_result(self.part + other.part)), self.name, self.tags, self.joints)

    def __and__(self, other):
        return self.__class__(bd.Part(self.wrap_result(self.part & other.part)), self.name, self.tags, self.joints)
