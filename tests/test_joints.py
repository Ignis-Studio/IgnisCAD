import pytest

import igniscad as icad


def test_join_named_joint_repositions_entity_center():
    screw = icad.Cylinder(1, 6)
    screw.add_joint("default", position=(0, 0, -3))
    plate = icad.Box(20, 20, 4)
    hole = plate.add_joint("hole", position=(5, -4, 2))

    aligned = screw.join(hole)

    assert pytest.approx(aligned.bbox.center().X) == 5.0
    assert pytest.approx(aligned.bbox.center().Y) == -4.0
    assert pytest.approx(aligned.bbox.center().Z) == 5.0


def test_joint_can_be_defined_from_bbox_face_center():
    box = icad.Box(10, 12, 14)
    top_joint = box.add_joint_on_face("top_mount", face="top", offset=2)

    assert pytest.approx(top_joint.position.X) == 0.0
    assert pytest.approx(top_joint.position.Y) == 0.0
    assert pytest.approx(top_joint.position.Z) == 9.0


def test_joints_survive_move_and_rotate():
    screw = icad.Cylinder(1, 6)
    screw.add_joint("default", position=(0, 0, -3))

    transformed = screw.move(10, 0, 0).rotate(z=90)

    assert "default" in transformed.joints
    default_joint = transformed.joint("default")
    assert pytest.approx(default_joint.position.X) == 10.0
    assert pytest.approx(default_joint.position.Y) == 0.0
    assert pytest.approx(default_joint.position.Z) == -3.0


def test_join_accepts_named_joint_lookup():
    peg = icad.Cylinder(1, 4)
    peg.add_joint("default", position=(0, 0, -2))
    target = icad.Box(10, 10, 2)
    target.add_joint("socket", position=(1, 2, 1))

    aligned = peg.join(target.joint("socket"), offset=(0, 0, 0.5))

    assert pytest.approx(aligned.joint("default").position.X) == 1.0
    assert pytest.approx(aligned.joint("default").position.Y) == 2.0
    assert pytest.approx(aligned.joint("default").position.Z) == 1.5
