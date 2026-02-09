import math
from igniscad import *

print(">>> Agent: Starting validation of Hole features...")

with Model("HoleTestBlock") as model:
    # 1. 创建基准块 (Base Block)
    # 尺寸: 100x50x20mm
    # 注意: Box 默认也是 align=CENTER，所以它的顶面在 Z = 10，底面在 Z = -10
    base_height = 20
    base = Box(100, 50, base_height, name="base_block")

    # 2. 准备左侧的沉头孔 (CounterBore)
    # 模拟场景: M6 内六角螺丝
    # 螺纹孔半径: 3mm
    # 螺丝头半径: 5.5mm
    # 螺丝头深度: 6mm
    # 高度: 设为 20mm (与板厚一致，因为你的逻辑是顶部对齐，所以能完美贯穿)
    print(">>> Agent: Designing CounterBore Hole (M6 Style)...")
    cb_hole = CounterBoreHole(
        radius=3,
        cb_radius=5.5,
        cb_depth=6,
        height=base_height,
        name="cb_feature"
    )
    # 移动到左侧 (-25, 0, 0)
    # 因为 Box 和 Hole 都是 Center 对齐且高度一致，所以 Z=0 无需调整即可顶面对齐
    cb_hole = cb_hole.move(-25, 0, 0)

    # 3. 准备右侧的埋头孔 (Countersink)
    # 模拟场景: M4 沉头螺丝 (90度)
    # 过孔半径: 2.2mm
    # 沉头最大半径: 4.5mm
    # 角度: 90度
    print(">>> Agent: Designing Countersink Hole (M4 90deg)...")
    csk_hole = CountersinkHole(
        radius=2.2,
        csk_radius=4.5,
        csk_angle=90,
        height=base_height,
        name="csk_feature"
    )
    # 移动到右侧 (25, 0, 0)
    csk_hole = csk_hole.move(25, 0, 0)

    # 4. 执行切割 (Boolean Subtraction)
    print(">>> Agent: Performing boolean cuts...")
    # 链式操作: 基座 - 沉头孔 - 埋头孔
    final_shape = base - cb_hole - csk_hole

    # 5. 提交结果
    model << final_shape

    # (可选) 在控制台输出计算出的锥孔深度，用于自我检查
    calculated_csk_depth = (4.5 - 2.2) / math.tan(math.radians(90 / 2))
    print(f">>> Agent Insight: The calculated depth for the 90° Countersink cone is {calculated_csk_depth:.2f}mm")

# 显示模型
show(model)