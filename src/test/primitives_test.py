import math
from igniscad import *

print(">>> Agent: Starting validation of Hole features...")

with Model("HoleTestBlock") as model:
    base_height = 20
    base = Box(100, 50, base_height, name="base_block")

    print(">>> Agent: Designing CounterBore Hole (M6 Style)...")
    cb_hole = CounterBoreHole(
        radius=3,
        cb_radius=5.5,
        cb_depth=6,
        height=base_height,
        name="cb_feature"
    )
    cb_hole = cb_hole.move(x=-25)

    print(">>> Agent: Designing Countersink Hole (M4 90deg)...")
    csk_hole = CountersinkHole(
        radius=2.2,
        csk_radius=4.5,
        csk_angle=90,
        height=base_height,
        name="csk_feature"
    )
    csk_hole = csk_hole.move(x=25)

    slot = Slot(38, 2, base_height, name="Slot").move(x=10).rotate(z=90).behind(base, offset=-38)

    print(">>> Agent: Performing boolean cuts...")
    final_shape = base - cb_hole - csk_hole
    model << final_shape - slot

    calculated_csk_depth = (4.5 - 2.2) / math.tan(math.radians(90 / 2))
    print(f">>> Agent Insight: The calculated depth for the 90° Countersink cone is {calculated_csk_depth:.2f}mm")

show(model)