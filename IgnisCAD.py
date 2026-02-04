import build123d as bd
import socketserver, webbrowser
import sys

# 1. 保存原始的错误处理方法，以免误伤其他真正的报错
_original_handle_error = socketserver.BaseServer.handle_error


def _silent_handle_error(self, request, client_address):
    """
    自定义的错误处理器：忽略连接中断错误，其他错误照常打印。
    """
    # 获取刚刚发生的异常
    exc_type, exc_value, _ = sys.exc_info()

    # 检查是否是 WinError 10053 (ConnectionAbortedError)
    # 或者是 BrokenPipeError (Linux/Mac 上常见的类似错误)
    if isinstance(exc_value, (ConnectionAbortedError, BrokenPipeError)):
        return  # 直接忽略，不打印任何东西

    # 如果是其他异常，调用原始方法（打印堆栈跟踪）
    _original_handle_error(self, request, client_address)


# 2. 应用补丁：替换标准库的错误处理方法
socketserver.BaseServer.handle_error = _silent_handle_error
_GLOBAL_LAST_PART = None


class ContextManager:
    """
    上下文管理器，负责捕获生成的模型。
    """

    def __init__(self, name):
        self.name = name
        self.part = None
        self.registry = {}

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
        用法: item << Cylinder(...) - Box(...)
        """
        if isinstance(other, Entity):
            self.part = self.part + other if self.part else other
            if other.name:
                self.registry[other.name] = other
        return self

    def find(self, name):
        return self.f(name)

    def f(self, name):
        if name in self.registry:
            return self.registry[name]
        raise ValueError(f"❌ Part '{name}' not found in this item.")


# --- 2. 实体封装 (Entity) ---
class Entity:
    def __init__(self, part: bd.Part, name=None):
        self.part = part
        self.name = name

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
    def _wrap_result(self, res):
        """内部辅助：强制打包结果为 Compound"""
        if not isinstance(res, (bd.Compound, bd.Solid)):
            res = bd.Compound(res)
        return res

    def __sub__(self, other):
        return self._wrap_result(self.part - other.part)

    def __add__(self, other):
        return self._wrap_result(self.part + other.part)

    def __and__(self, other):
        return self._wrap_result(self.part & other.part)

    # --- 4. 尺寸与语义感知 (新增) ---
    @property
    def bbox(self):
        """获取包围盒，方便计算相对位置"""
        return self.part.bounding_box()

    @property
    def top(self):
        """获取顶面中心点 Z 坐标"""
        return self.bbox.max.Z

    @property
    def right(self):
        """获取最右侧 X 坐标"""
        return self.bbox.max.X

    @property
    def radius(self):
        """尝试估算半径 (仅针对圆柱/圆球等)"""
        # 简单逻辑：X 方向宽度的一半
        return self.bbox.size.X / 2

    # --- 5. 通用语义对齐 (Universal Align) ---
    def align(self, target, face="top", offset=0):
        """
        语义化对齐：将当前物体“吸附”到目标物体的指定面上。
        原理：计算目标面的中心，加上自身一半的厚度，实现无缝堆叠。

        Args:
            target (Entity): 目标物体
            face (str): "top", "bottom", "left", "right", "front", "back"
            offset (float): 额外的间隙（正数=远离，负数=嵌入）
        """
        if not isinstance(target, Entity):
            raise ValueError("Target must be an Entity")

        # 1. 获取包围盒信息
        t_box = target.bbox  # Target Bounding Box
        s_box = self.bbox  # Self Bounding Box (Current)

        # 2. 默认目标位置为 Target 的中心点
        # (如果不修改某轴坐标，默认就是中心对齐)
        dest_x = t_box.center().X
        dest_y = t_box.center().Y
        dest_z = t_box.center().Z

        # 3. 自身尺寸 (宽、深、高)
        s_w = s_box.size.X
        s_d = s_box.size.Y
        s_h = s_box.size.Z

        # 4. 根据 Face 修改目标坐标
        # 逻辑：目标面坐标 +/- 自身一半尺寸 +/- 额外偏移
        f = face.lower()

        # Z轴 (上下)
        if f == "top":
            dest_z = t_box.max.Z + (s_h / 2) + offset
        elif f == "bottom":
            dest_z = t_box.min.Z - (s_h / 2) - offset

        # X轴 (左右)
        elif f == "right":
            dest_x = t_box.max.X + (s_w / 2) + offset
        elif f == "left":
            dest_x = t_box.min.X - (s_w / 2) - offset

        # Y轴 (前后) - 注意：CAD中通常 Y+ 是后(Back/North), Y- 是前(Front/South)
        elif f == "back":
            dest_y = t_box.max.Y + (s_d / 2) + offset
        elif f == "front":
            dest_y = t_box.min.Y - (s_d / 2) - offset
        else:
            raise ValueError(f"Unknown face: {face}. Use top/bottom/left/right/front/back")

        # 5. 计算位移向量 (目标中心 - 当前中心)
        # 这一步至关重要，因为物体当前不一定在原点
        curr_x = s_box.center().X
        curr_y = s_box.center().Y
        curr_z = s_box.center().Z

        dx = dest_x - curr_x
        dy = dest_y - curr_y
        dz = dest_z - curr_z

        return self.move(dx, dy, dz)

    # --- 6. 语义糖 (Syntactic Sugar for AI) ---
    # 让 AI 写出类似自然语言的代码

    def on_top_of(self, target, offset=0):
        return self.align(target, "top", offset)

    def under(self, target, offset=0):
        return self.align(target, "bottom", offset)

    def right_of(self, target, offset=0):
        return self.align(target, "right", offset)

    def left_of(self, target, offset=0):
        return self.align(target, "left", offset)

    def in_front_of(self, target, offset=0):
        return self.align(target, "front", offset)

    def behind(self, target, offset=0):
        return self.align(target, "back", offset)


# --- 3. 顶层 API 函数 ---

def Item(name):
    """创建上下文的工厂函数"""
    return ContextManager(name)


def show():
    """
    尝试连接 Yet Another CAD Viewer (浏览器)，
    如果失败（未安装或报错），则直接保存并打开 STL。
    """
    global _GLOBAL_LAST_PART
    if not _GLOBAL_LAST_PART:
        print("⚠️ Nothing to show! (Did you forget to use 'item << ...'?)")
        return

    label = _GLOBAL_LAST_PART.label or "Model"
    print(f"👀 Processing: {label}")

    # 1. 尝试连接 Yet Another CAD Viewer (YACV)
    try:
        from yacv_server import show as yacv_show
        target_obj = _GLOBAL_LAST_PART
        yacv_show(target_obj, names=[label])

        url = "http://localhost:32323"
        print(f"✅ Sent to YACV (Check your browser, at {url})")
        webbrowser.open(url)
        input("✅ Press Enter to exit...")
        return
    except Exception as e:
        print(f"⚠️ Failed to connect to YACV: {e}")

    # 2. 如果上面失败了，直接导出 STL 文件
    print("⚠️ Viewer not available. Exporting to disk...")

    # 导出 STL
    filename = f"{label}.stl"

    try:
        bd.export_stl(_GLOBAL_LAST_PART, filename)
    except NameError:
        import build123d as bd_fallback
        bd_fallback.export_stl(_GLOBAL_LAST_PART, filename)

    import os
    abs_path = os.path.abspath(filename)
    print(f"💾 Saved: {abs_path}")
    print("👉 You can open this file with Windows 3D Viewer.")

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

class Group(Entity):
    """
    逻辑分组：将多个实体组合成一个单一实体。
    支持上下文管理器语法，组内的物体会自动进行布尔并集 (Union)。
    一旦退出 with 块，该 Group 对象即可像普通 Entity 一样被移动或对齐。
    """

    def __init__(self, name=None):
        # 初始化时没有内部零件，设为 None
        # 注意：在添加第一个零件前调用 move/rotate 会报错，这是预期的行为
        super().__init__(None, name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 退出 with 块时不需要额外操作
        # 因为 self.part 已经在 __lshift__ 中实时更新了
        pass

    def __lshift__(self, other):
        """
        重载 '<<' 操作符，用于向组内添加物体。
        执行逻辑：Union (并集)
        """
        if isinstance(other, Entity):
            if self.part is None:
                # 这是一个新组，第一个物体直接作为基础
                self.part = other.part
            else:
                # 组内已有物体，将新物体与现有物体融合 (Fuse/Union)
                self.part = self.part + other.part
        else:
            raise ValueError("❌ Group implies adding Entity objects (Box, Cylinder, etc.)")

        return self  # 允许链式调用: g << part1 << part2
