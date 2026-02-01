import build123d as bd
_GLOBAL_LAST_PART = None


class ContextManager:
    """
    上下文管理器，负责捕获生成的模型。
    """

    def __init__(self, name):
        self.name = name
        self.part = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 退出 with 块时，把当前零件保存到全局变量，供 show() 使用
        global _GLOBAL_LAST_PART
        if self.part:
            self.part.label = self.name  # 给零件打上标签
            _GLOBAL_LAST_PART = self.part
        return False

    def __lshift__(self, other):
        """
        重载 '<<' 操作符。
        这是实现 "无变量赋值" 的关键魔法。
        用法: item << Cylinder(...) - Box(...)
        """
        if isinstance(other, Entity):
            self.part = other
        return self.part  # 允许链式调用


# --- 2. 实体封装 (Entity) ---
# 保持之前的逻辑，但增加 name 支持
class Entity:
    def __init__(self, part: bd.Part, name=None):
        self.part = part
        self.name = name  # 仅仅为了元数据，不影响计算

    # --- 变换逻辑 ---
    def move(self, x=0, y=0, z=0):
        return Entity(self.part.moved(bd.Location((x, y, z))), self.name)

    def rotate(self, x=0, y=0, z=0):
        # 链式旋转
        p = self.part
        if x: p = p.rotate(bd.Axis.X, x)
        if y: p = p.rotate(bd.Axis.Y, y)
        if z: p = p.rotate(bd.Axis.Z, z)
        return Entity(p, self.name)

    # --- 布尔运算 ---
    def __sub__(self, other):
        return Entity(self.part - other.part)

    def __add__(self, other):
        return Entity(self.part + other.part)

    def __and__(self, other):
        return Entity(self.part & other.part)


# --- 3. 顶层 API 函数 ---

def Item(name):
    """创建上下文的工厂函数"""
    return ContextManager(name)


def show():
    """全局 show 函数，自动寻找刚才定义的零件"""
    global _GLOBAL_LAST_PART
    if _GLOBAL_LAST_PART:
        print(f"👀 Rendering: {_GLOBAL_LAST_PART.label}")
        try:
            from ocp_vscode import show as ocp_show
            # 渲染底层的 part 对象
            ocp_show(_GLOBAL_LAST_PART.part, names=[_GLOBAL_LAST_PART.label])
        except ImportError:
            filename = f"{_GLOBAL_LAST_PART.label}.stl"
            _GLOBAL_LAST_PART.part.export_stl(filename)
            print(f"Scanner saved to {filename}")
    else:
        print("⚠️ Nothing to show! Did you forget to use '<<' ?")

# --- 2. 原语工厂 (Primitives) ---
# AI 只需要调用这些简单的函数，不需要处理复杂的 build123d 参数

def Box(x, y, z, name=None) -> Entity:
    # 默认居中对齐，方便 AI 这种直觉动物
    return Entity(bd.Part(bd.Box(x, y, z, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))), name)

def Cylinder(r, h, name=None) -> Entity:
    return Entity(bd.Part(bd.Cylinder(radius=r, height=h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))), name)

def Sphere(r, name=None) -> Entity:
    return Entity(bd.Part(bd.Sphere(radius=r)), name)

def Torus(major, minor, name=None) -> Entity:
    return Entity(bd.Part(bd.Torus(major_radius=major, minor_radius=minor)), name)


# --- 3. 上下文管理器 (Contexts) ---
# 用于处理“一组物体”的关系，避免重复写坐标计算

class Group:
    """
    逻辑分组。
    在 with 块内部定义的任何运算不会自动发生，
    这里主要为了代码折叠和逻辑清晰，或者未来扩展局部坐标系。
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass