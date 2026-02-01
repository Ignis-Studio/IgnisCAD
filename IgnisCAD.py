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
    """
    能连上 VSCode 就连，连不上就直接保存 STL。
    不报错，不废话。
    """
    global _GLOBAL_LAST_PART
    if not _GLOBAL_LAST_PART:
        print("⚠️ Nothing to show! (Did you use 'item << ...'?)")
        return

    label = _GLOBAL_LAST_PART.label or "Model"
    print(f"👀 Processing: {label}")
    
    # 尝试连接 VS Code (ocp_vscode)
    try:
        from ocp_vscode import show as ocp_show
        # 去掉所有花哨参数，回归最原始的调用
        # 如果 VS Code 插件没开，这里会稍作停顿然后报错或无反应
        ocp_show(_GLOBAL_LAST_PART.part, names=[label])
        print(f"✅ Sent to VS Code Viewer (Check your VS Code window)")
        return
    except Exception:
        # 这里的异常可能是 ImportError (没装库) 或 RuntimeError (连不上)
        # 我们不在乎具体原因，直接降级
        pass

    # 如果上面失败了，直接导出文件
    print("⚠️ Viewer not available. Exporting to disk...")
    
    # 导出 STL
    filename = f"{label}.stl"
    bd.export_stl(_GLOBAL_LAST_PART.part, filename)
    
    import os
    abs_path = os.path.abspath(filename)
    print(f"💾 Saved: {abs_path}")
    print("👉 You can open this file with Windows 3D Viewer.")
    
    # 【可选】如果你在 Windows 上，这行代码会自动尝试打开它
    try:
        os.startfile(abs_path)
    except:
        pass

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