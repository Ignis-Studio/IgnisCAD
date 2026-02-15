"""
Mixin classes.
Contains Syntactic Sugar and Syntactic Properties.
"""
import build123d as bd
from typing import TYPE_CHECKING

from igniscad.selectors import FaceSelector, EdgeSelector, VertexSelector

if TYPE_CHECKING:
    from igniscad.core import Entity

class EntitySelectorMixin:
    """
    A mixin for the Entity class that provides methods to initiate selections.

    This mixin adds the .faces(), .edges(), and .vertices() methods to the
    Entity class, which are the entry points for the fluent selection API.
    """
    def faces(self) -> FaceSelector:
        """Selects all faces of the entity.

        This method retrieves all faces from the underlying build123d part
        and wraps them in a FaceSelector, enabling chainable filtering and
        modification.

        Returns:
            FaceSelector: A selector containing all faces of the entity.
        """
        if TYPE_CHECKING:
            assert isinstance(self, Entity)
        return FaceSelector(self.part.faces(), parent=self)

    def edges(self) -> EdgeSelector:
        """Selects all edges of the entity.

        This method retrieves all edges from the underlying build123d part
        and wraps them in an EdgeSelector, enabling chainable filtering and
        modification.

        Returns:
            EdgeSelector: A selector containing all edges of the entity.
        """
        if TYPE_CHECKING:
            assert isinstance(self, Entity)
        return EdgeSelector(self.part.edges(), parent=self)

    def vertices(self) -> VertexSelector:
        """Selects all vertices of the entity.

        This method retrieves all vertices from the underlying build123d part
        and wraps them in a VertexSelector, enabling chainable filtering and
        modification.

        Returns:
            VertexSelector: A selector containing all vertices of the entity.
        """
        if TYPE_CHECKING:
            assert isinstance(self, Entity)
        return VertexSelector(self.part.vertices(), parent=self)

class AlignmentMixin:
    """
    A mixin of class Entity, specified to calculate alignment, bounding box and position.
    """
    # Syntactic properties
    @property
    def bbox(self):
        """Grabbing the bounding box of the entity."""
        if TYPE_CHECKING:
            assert isinstance(self, Entity)
        return self.wrap_result(self.part).bounding_box()

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

        if TYPE_CHECKING:
            assert isinstance(self, Entity)
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

class ModificationMixin:
    """
    A mixin of class Entity, specified to perform modification operations.
    """
    def fillet(self, radius, edges=None):
        """
        Fillets the edges of the entity.

        Args:
            radius (float): The radius of the fillet.
            edges (list, optional): A list of edges to fillet. If None, all edges are filleted. Defaults to None.
        """
        if TYPE_CHECKING:
            assert isinstance(self, Entity)
        
        edges_to_fillet = edges
        if edges_to_fillet is None:
            edges_to_fillet = self.part.edges()
        
        # Convert primitive to a generic Solid by using its .wrapped property
        part_as_solid = bd.Solid(self.part.wrapped)
        new_part = part_as_solid.fillet(radius, edge_list=edges_to_fillet)
        return self.__class__(self.wrap_result(new_part), self.name, self.tags)

    def chamfer(self, distance, edges=None):
        """
        Chamfers the edges of the entity.

        Args:
            distance (float): The distance of the chamfer.
            edges (list, optional): A list of edges to chamfer. If None, all edges are chamfered. Defaults to None.
        """
        if TYPE_CHECKING:
            assert isinstance(self, Entity)

        edges_to_chamfer = edges
        if edges_to_chamfer is None:
            edges_to_chamfer = self.part.edges()

        # Convert primitive to a generic Solid by using its .wrapped property
        part_as_solid = bd.Solid(self.part.wrapped)
        new_part = part_as_solid.chamfer(distance, distance, edge_list=edges_to_chamfer)
        return self.__class__(self.wrap_result(new_part), self.name, self.tags)

    def shell(self):
        """
        Creates a shell of the entity.
        """
        if TYPE_CHECKING:
            assert isinstance(self, Entity)

        shell_obj = self.part.shell()
        
        return self.__class__(shell_obj, self.name, self.tags)

    def offset(self, distance, kind=bd.Kind.ARC):
        """
        Offsets the entity.

        Args:
            distance (float): The distance to offset.
            kind (str, optional): The kind of offset to perform. Defaults to 'arc'.
        """
        if TYPE_CHECKING:
            assert isinstance(self, Entity)

        try:
            new_part = bd.offset(self.part, amount=distance, kind=kind)
        except RuntimeError as e:
            if "Unexpected result type" in str(e):
                # This error can happen with complex sketches like text, where offsetting
                # a character results in a shape that build123d doesn't expect.
                # The workaround is to offset each face of the compound individually
                # and combine the results, skipping any faces that fail to offset.
                all_faces = self.part.faces()
                offset_faces = []
                for face in all_faces:
                    try:
                        # Each face of a text object is a letter.
                        offset_result = bd.offset(face, amount=distance, kind=kind)
                        if isinstance(offset_result, bd.Face):
                            offset_faces.append(offset_result)
                        elif isinstance(offset_result, bd.Compound):
                            offset_faces.extend(offset_result.faces())
                    except RuntimeError:
                        pass

                if not offset_faces:
                    raise RuntimeError("Offset operation failed for all faces.") from e

                new_part = bd.Sketch(offset_faces)
            else:
                raise e

        return self.__class__(self.wrap_result(new_part), self.name, self.tags)
