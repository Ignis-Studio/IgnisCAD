from IgnisCAD import *

if __name__ == "__main__":
    with Item("Flange") as item:
        item << Cylinder(name="base", r=50, h=10)
        item << Cylinder(name="bolt", r=5, h=20).move(x=item.f("base").radius * 0.8)
        item << item.f("base") - item.f("bolt")
    show()