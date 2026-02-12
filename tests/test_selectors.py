"""
Pytest for the new selector features.
"""

import pytest
import build123d as bd
from igniscad import Box, Entity

@pytest.fixture
def sample_box() -> Entity:
    """Create a 10x10x10 box for testing."""
    return Box(10, 10, 10, name="test_box")

def test_positional_selectors(sample_box: Entity):
    """Test positional selectors like top(), bottom()."""
    top_face = sample_box.faces().top().first
    assert top_face is not None
    assert top_face.center().Z == 5.0

    bottom_face = sample_box.faces().bottom().first
    assert bottom_face is not None
    assert bottom_face.center().Z == -5.0

def test_topological_selectors(sample_box: Entity):
    """Test topological selectors like sort_by_area()."""
    # All faces of a cube have the same area
    sorted_faces = sample_box.faces().sort_by_area().get()
    assert len(sorted_faces) == 6
    assert all(pytest.approx(f.area) == 100.0 for f in sorted_faces)

    # Test with a more complex shape
    box1 = Box(10, 10, 10)
    box2 = Box(5, 5, 5).move(0, 0, 10)
    shape = box1 + box2
    
    largest_face = shape.faces().sort_by_area(reverse=True).first
    assert largest_face is not None
    # Allow for small floating point inaccuracies
    assert pytest.approx(largest_face.area) == 100.0

    smallest_face = shape.faces().sort_by_area().first
    assert smallest_face is not None
    assert pytest.approx(smallest_face.area) == 25.0

def test_filtering(sample_box: Entity):
    """Test filtering by axis."""
    from igniscad.selectors import Axis
    
    faces_in_positive_z = sample_box.faces().filter_by(Axis.Z).get()
    # Only the top face should be in the positive Z half
    assert len(faces_in_positive_z) == 1
    assert faces_in_positive_z[0].center().Z == 5.0

def test_chaining_modification(sample_box: Entity):
    """Test chaining a modification after selection."""
    filleted_box = sample_box.faces().top().fillet(1)
    
    # Check that the operation was successful and returned a new Entity
    assert isinstance(filleted_box, Entity)
    
    # A simple check: the new part should have more edges than the original
    assert len(filleted_box.part.edges()) > len(sample_box.part.edges())

def test_tagging_system(sample_box: Entity):
    """Test the tagging system."""
    # Tag the top face
    sample_box.faces().top().tag("top_surface")
    
    # Retrieve the tagged face
    tagged_selector = sample_box.get_by_tag("top_surface")
    assert len(tagged_selector) == 1
    
    tagged_face = tagged_selector.first
    assert tagged_face is not None
    assert tagged_face.center().Z == 5.0

    # Test that tags are preserved after a modification
    filleted_box = sample_box.faces().top().fillet(1)
    
    # The tag should still exist on the new object
    tagged_selector_after_fillet = filleted_box.get_by_tag("top_surface")
    assert len(tagged_selector_after_fillet) == 1
    
    # Note: The original face object is not guaranteed to be the same instance
    # after the modification, so we check its properties instead.
    tagged_face_after_fillet = tagged_selector_after_fillet.first
    assert tagged_face_after_fillet is not None
    assert tagged_face_after_fillet.center().Z == 5.0

def test_empty_selector(sample_box: Entity):
    """Test that selectors handle empty lists gracefully."""
    empty_selector = sample_box.faces().filter_by(lambda f: f.area > 200)
    assert len(empty_selector) == 0
    assert empty_selector.top().first is None
    assert empty_selector.sort_by_area().get() == []
