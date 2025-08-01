"""
新增接口：
- add_wall: 直接添加墙体对象，支持自定义大小和位置，自动做碰撞检测与grid map更新。
- check_path_collision_with_grid: 检查轨迹Path是否与grid map障碍发生碰撞。
"""
# 地图编辑相关通用方法
import os
import json
from core.data_structures import MapRepresentation, MapObject, Path, SourceType
from utils.config import config
from typing import Tuple, List
from processors.geometry_processor import generate_grid_map_from_objects
import numpy as np

def create_map(map_id: str, canvas_size: Tuple[float, float], source_type: SourceType = SourceType.OTHER) -> MapRepresentation:
    """
    新建地图对象
    """
    return MapRepresentation(
        map_id=map_id,
        source_type=source_type,
        objects={},
        grid_map=None,
        scene_description="",
        canvas_size=canvas_size,
    )

def load_existing_map(map_file_path: str = "data/maps/complete_indoor_scene.json") -> MapRepresentation:
    """
    加载已保存的地图文件
    
    Args:
        map_file_path: 地图文件路径
        
    Returns:
        MapRepresentation对象
        
    Raises:
        FileNotFoundError: 地图文件不存在
        Exception: 加载地图失败
    """
    if not os.path.exists(map_file_path):
        raise FileNotFoundError(f"地图文件不存在: {map_file_path}")
    
    try:
        map_rep = MapRepresentation.load_from_json(map_file_path)
        return map_rep
    except Exception as e:
        raise Exception(f"加载地图失败: {e}")

def add_object_from_file(map_rep: MapRepresentation, object_ref: str, new_position: Tuple[float, float, float] = (0.0, 0.0, 0.0), object_dir: str = "data/objects"):
    """
    通过引用物体名称或路径，自动加载物体配置文件并添加到地图，支持指定新位置。
    
    Args:
        map_rep: 地图表示对象
        object_ref: 物体引用（文件名或完整路径）
        new_position: 物体位置 (x, y, z)，默认为 (0.0, 0.0, 0.0)
        object_dir: 物体文件目录，默认为 "data/objects"
        
    Raises:
        FileNotFoundError: 物体配置文件不存在
    """
    if os.path.isfile(object_ref):
        path = object_ref
    else:
        path = os.path.join(object_dir, f"{object_ref}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"物体配置文件不存在: {path}")
    
    obj = MapObject.load_from_json(path)
    # 设置位置（使用默认值或指定值）
    obj.position = new_position
    
    # 保证id唯一，避免覆盖
    base_id = obj.id
    i = 1
    new_id = base_id
    while new_id in map_rep.objects:
        i += 1
        new_id = f"{base_id}_{i}"
    obj.id = new_id
    map_rep.objects[new_id] = obj

def add_object(map_rep: MapRepresentation, map_object: MapObject):
    map_rep.objects[map_object.id] = map_object

def add_path(map_rep: MapRepresentation, path: Path, path_id: str = None):
    # 轨迹作为特殊物体加入，或可扩展为单独属性
    if path_id is None:
        path_id = f"path_{len(map_rep.objects)}"
    obj = MapObject(
        label="path",
        size=(0.0, 0.0, 0.0),
        position=(0.0, 0.0, 0.0),
        id=path_id,
    )
    # 直接挂载轨迹点集，便于可视化
    obj.footprint_2d = path.points
    map_rep.objects[path_id] = obj

def set_canvas_size(map_rep: MapRepresentation, canvas_size: Tuple[float, float]):
    map_rep.canvas_size = canvas_size

def check_collision_with_grid(map_rep: MapRepresentation, map_object: MapObject, resolution: float = None) -> bool:
    """
    检查新物体与现有grid map是否有重叠（2D bbox），如有重叠则进一步判断高度。
    返回True表示有不可叠加的碰撞，False表示可添加。
    """
    if resolution is None:
        resolution = config.get_default_resolution()
    
    if map_rep.grid_map is None:
        return False
    min_x, min_y, max_x, max_y = map_object.get_bbox_2d()
    width, height = map_rep.canvas_size
    grid_h, grid_w = map_rep.grid_map.shape  # (行,列)=(y,x)
    for row in range(grid_h):
        for col in range(grid_w):
            x = (col + 0.5) * resolution
            y = (row + 0.5) * resolution
            if (min_x <= x <= max_x) and (min_y <= y <= max_y) and map_rep.grid_map[row, col] == 0:
                # 找到重叠区域，判断高度
                for obj in map_rep.objects.values():
                    omin_x, omin_y, omax_x, omax_y = obj.get_bbox_2d()
                    if (omin_x <= x <= omax_x) and (omin_y <= y <= omax_y):
                        z_min1, z_max1 = map_object.get_bbox_3d()[2], map_object.get_bbox_3d()[5]
                        z_min2, z_max2 = obj.get_bbox_3d()[2], obj.get_bbox_3d()[5]
                        if not (z_max1 <= z_min2 or z_min1 >= z_max2):
                            return True
    return False

def update_grid_map_incremental(map_rep: MapRepresentation, map_object: MapObject, resolution: float = None):
    """
    增量更新grid map，只添加新物体的障碍区域。
    """
    if resolution is None:
        resolution = config.get_default_resolution()
    
    if map_rep.grid_map is None:
        # 没有grid map，先全量生成
        map_rep.grid_map = generate_grid_map_from_objects(map_rep, resolution)
        return
        
    min_x, min_y, max_x, max_y = map_object.get_bbox_2d()
    grid_h, grid_w = map_rep.grid_map.shape
    for row in range(grid_h):
        for col in range(grid_w):
            x = (col + 0.5) * resolution
            y = (row + 0.5) * resolution
            if (min_x <= x <= max_x) and (min_y <= y <= max_y):
                map_rep.grid_map[row, col] = 0

def update_grid_map_full(map_rep: MapRepresentation, resolution: float = None):
    """
    全量更新grid map，遍历所有物体。
    使用0.01精度，并自动保存为PNG文件。
    """
    if resolution is None:
        resolution = config.get_default_resolution()  # 现在默认是0.01
    
    map_rep.grid_map = generate_grid_map_from_objects(map_rep, resolution)

def add_object_with_collision_check(map_rep: MapRepresentation, object_ref: str, new_position: Tuple[float, float, float] = (0.0, 0.0, 0.0), object_dir: str = "data/objects", resolution: float = None):
    """
    通过文件引用添加物体，添加前做碰撞检测，成功后增量更新grid map，支持指定位置。
    
    Args:
        map_rep: 地图表示对象
        object_ref: 物体引用（文件名或完整路径）
        new_position: 物体位置 (x, y, z)，默认为 (0.0, 0.0, 0.0)
        object_dir: 物体文件目录，默认为 "data/objects"
        resolution: 栅格地图分辨率，默认为配置中的默认值
        
    Raises:
        FileNotFoundError: 物体配置文件不存在
        ValueError: 发生碰撞
    """
    if resolution is None:
        resolution = config.get_default_resolution()
    
    # 先加载物体但不加入map_rep
    if os.path.isfile(object_ref):
        path = object_ref
    else:
        path = os.path.join(object_dir, f"{object_ref}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"物体配置文件不存在: {path}")
    
    obj = MapObject.load_from_json(path)
    # 设置位置（使用默认值或指定值）
    obj.position = new_position
    
    # 保证id唯一，避免覆盖
    base_id = obj.id
    i = 1
    new_id = base_id
    while new_id in map_rep.objects:
        i += 1
        new_id = f"{base_id}_{i}"
    obj.id = new_id
    
    # 碰撞检测
    if check_collision_with_grid(map_rep, obj, resolution):
        raise ValueError("物体与现有物体发生不可叠加的碰撞，添加失败！")
    
    # 添加物体
    map_rep.objects[new_id] = obj
    # 增量更新grid map
    update_grid_map_incremental(map_rep, obj, resolution)

def add_wall(map_rep: MapRepresentation, wall_id: str, size: Tuple[float, float, float], position: Tuple[float, float, float], resolution: float = None):
    """
    直接添加墙体对象（无需json文件），自动做碰撞检测与grid map更新。
    墙体有特殊的碰撞检测逻辑：允许与其他墙体重叠，但不与家具重叠。
    """
    if resolution is None:
        resolution = config.get_default_resolution()
    
    wall_obj = MapObject(
        label="wall",
        size=size,
        position=position,
        id=wall_id,
    )
    
    # 墙体特殊的碰撞检测：只检查与家具的碰撞，不检查与其他墙体的碰撞
    if check_wall_collision_with_furniture(map_rep, wall_obj, resolution):
        raise ValueError("墙体与家具发生碰撞，添加失败！")
    
    # 保证id唯一
    base_id = wall_obj.id
    i = 1
    new_id = base_id
    while new_id in map_rep.objects:
        i += 1
        new_id = f"{base_id}_{i}"
    wall_obj.id = new_id
    map_rep.objects[new_id] = wall_obj
    update_grid_map_incremental(map_rep, wall_obj, resolution)
    return new_id

def check_wall_collision_with_furniture(map_rep: MapRepresentation, wall_object: MapObject, resolution: float = None) -> bool:
    """
    检查墙体与家具的碰撞，墙体之间允许重叠。
    返回True表示有不可叠加的碰撞，False表示可添加。
    """
    if resolution is None:
        resolution = config.get_default_resolution()
    
    if map_rep.grid_map is None:
        return False
    
    min_x, min_y, max_x, max_y = wall_object.get_bbox_2d()
    width, height = map_rep.canvas_size
    grid_h, grid_w = map_rep.grid_map.shape  # (行,列)=(y,x)
    
    for row in range(grid_h):
        for col in range(grid_w):
            x = (col + 0.5) * resolution
            y = (row + 0.5) * resolution
            if (min_x <= x <= max_x) and (min_y <= y <= max_y) and map_rep.grid_map[row, col] == 0:
                # 找到重叠区域，检查是否与家具重叠
                for obj in map_rep.objects.values():
                    # 跳过其他墙体
                    if obj.label == "wall":
                        continue
                    
                    omin_x, omin_y, omax_x, omax_y = obj.get_bbox_2d()
                    if (omin_x <= x <= omax_x) and (omin_y <= y <= omax_y):
                        # 检查高度重叠
                        z_min1, z_max1 = wall_object.get_bbox_3d()[2], wall_object.get_bbox_3d()[5]
                        z_min2, z_max2 = obj.get_bbox_3d()[2], obj.get_bbox_3d()[5]
                        if not (z_max1 <= z_min2 or z_min1 >= z_max2):
                            return True
    return False


def check_path_collision_with_grid(map_rep: MapRepresentation, path: Path, resolution: float = None, sample_step: float = None) -> bool:
    """
    检查轨迹Path的线段与grid map障碍是否发生碰撞。
    对每一段线段采样若干点，若有点落在障碍格上则判为碰撞。
    """
    if resolution is None:
        resolution = config.get_default_resolution()
    if sample_step is None:
        sample_step = config.get_sample_step()
    
    if map_rep.grid_map is None:
        return False
    grid_h, grid_w = map_rep.grid_map.shape
    points = path.points
    for idx in range(len(points) - 1):
        x0, y0 = points[idx]
        x1, y1 = points[idx + 1]
        dx = x1 - x0
        dy = y1 - y0
        dist = (dx ** 2 + dy ** 2) ** 0.5
        steps = max(2, int(dist / sample_step) + 1)
        for s in range(steps + 1):
            t = s / steps
            x = x0 + t * dx
            y = y0 + t * dy
            col = int(x // resolution)
            row = int(y // resolution)
            if 0 <= row < grid_h and 0 <= col < grid_w:
                if map_rep.grid_map[row, col] == 0:
                    return True
    return False
