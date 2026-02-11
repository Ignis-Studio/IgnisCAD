import igniscad as ic


def test_box_cylinder_boolean_ops_return_entity():
    a = ic.Box(10, 10, 10, name="a")
    b = ic.Cylinder(3, 12, name="b")

    sub = a - b
    inter = a & b

    assert sub.part is not None
    assert inter.part is not None


def test_move_rotate_chain_works():
    e = ic.Box(4, 5, 6).move(1, 2, 3).rotate(x=15, y=30, z=45)
    assert e.part is not None
