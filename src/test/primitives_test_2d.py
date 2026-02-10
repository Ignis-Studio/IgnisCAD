from igniscad import *


def create_nameplate():
    """Creates a 3D nameplate model."""
    plate_sketch = Rectangle(x=138, y=40, name="plate_sketch")
    plate_part = Extrude(plate_sketch, amount=5, name="plate")
    text_sketch = Text("Supports non-ASCII letters!", font_size=10, name="text_sketch")
    text_part = Extrude(text_sketch, amount=2, name="text_geom")

    text_part = text_part.on_top_of(plate_part)
    with Group("Final") as final:
        final << plate_part << text_part

    return final

if __name__ == "__main__":
    with Model("test") as model:
        model << create_nameplate()
    show(model)

