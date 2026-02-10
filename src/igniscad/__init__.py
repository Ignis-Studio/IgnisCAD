from igniscad.core import *
from igniscad.containers import *
from igniscad.primitives import *
from igniscad.primitives_2d import *
from igniscad.visualization import show

from igniscad._err_handler import wrap_handlers
from igniscad._logger_handler import setup
wrap_handlers() # Apply the error handler patch.
setup(__name__)

__all__ = ['Model', 'Group', # Containers
           'Box', 'Sphere', 'Cylinder', 'Torus', "Slot", "ISO_Hole", "CounterBoreHole", "CountersinkHole", # Primitives
           'Rectangle', 'Circle', 'Polygon', 'Text', 'Extrude', 'Revolve', 'Sweep', 'Loft', # 2D Primitives
           'show', # Visualization
           'AlignmentMixin', # Mixins
           'Entity' # Base wrapper
        ]
