"""
Mixin classes.
Contains Syntactic Sugar and Syntactic Properties.
"""

class AlignmentMixin:
    """
    A mixin of class Entity, specified to calculate alimentation, bounding box and position.
    """
    # Syntactic properties
    @property
    def bbox(self):
        """Grabbing the bounding box of the entity."""
        return self._wrap_result(self.part).bounding_box()

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