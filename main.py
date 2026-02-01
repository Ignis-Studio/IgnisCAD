from IgnisCAD import *

if __name__ == "__main__":
    with Item("TestFlange") as item:
        # AI 的逻辑：底座 减去 (螺栓 移动 旋转)
        # 不需要中间变量，一气呵成
        item << Cylinder(name="base", r=50, h=10) - Cylinder(r=5, h=20).move(x=40).rotate(z=90)

    show()