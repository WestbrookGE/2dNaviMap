# 地图编辑相关通用方法
import os
import json
from core.data_structures import MapRepresentation, MapObject, Path, SourceType
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

def add_object_from_file(map_rep: MapRepresentation, object_ref: str, object_dir: str = "data/objects", new_position: Tuple[float, float, float] = None):
    """
    通过引用物体名称或路径，自动加载物体配置文件并添加到地图，支持指定新位置。
    """
    if os.path.isfile(object_ref):
        path = object_ref
    else:
        path = os.path.join(object_dir, f"{object_ref}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"物体配置文件不存在: {path}")
    obj = MapObject.load_from_json(path)
    if new_position is not None:
        obj.position = new_position
        x, y, z = new_position
        w, d, h = obj.size
        obj.source_bbox_3d = (
            x, y, z,
            x + w, y + d, z + h
        )
        obj.source_centroid_3d = (x + w/2, y + d/2, z + h/2)
        obj.bbox_2d = (x, y, x + w, y + d)
    # 保证object_id唯一，避免覆盖
    base_id = obj.object_id
    i = 1
    new_id = base_id
    while new_id in map_rep.objects:
        i += 1
        new_id = f"{base_id}_{i}"
    obj.object_id = new_id
    map_rep.objects[new_id] = obj

def add_object(map_rep: MapRepresentation, map_object: MapObject):
    map_rep.objects[map_object.object_id] = map_object

def add_path(map_rep: MapRepresentation, path: Path, path_id: str = None):
    # 轨迹作为特殊物体加入，或可扩展为单独属性
    if path_id is None:
        path_id = f"path_{len(map_rep.objects)}"
    map_rep.objects[path_id] = MapObject(
        object_id=path_id,
        category="path",
        source_bbox_3d=(0,0,0,0,0,0),
        source_centroid_3d=(0,0,0),
        footprint_2d=path.points,
        attributes=["path"],
    )

def set_canvas_size(map_rep: MapRepresentation, canvas_size: Tuple[float, float]):
    map_rep.canvas_size = canvas_size

def check_collision_with_grid(map_rep: MapRepresentation, map_object: MapObject, resolution: float = 1.0) -> bool:
    """
    检查新物体与现有grid map是否有重叠（2D bbox），如有重叠则进一步判断高度。
    返回True表示有不可叠加的碰撞，False表示可添加。
    """
    if map_rep.grid_map is None:
        return False
    min_x, min_y, max_x, max_y = map_object.bbox_2d
    width, height = map_rep.canvas_size
    grid_w, grid_h = map_rep.grid_map.shape
    for i in range(grid_w):
        for j in range(grid_h):
            x = (i + 0.5) * resolution
            y = (j + 0.5) * resolution
            if (min_x <= x <= max_x) and (min_y <= y <= max_y) and map_rep.grid_map[i, j] == 0:
                # 找到重叠区域，判断高度
                for obj in map_rep.objects.values():
                    if hasattr(obj, 'bbox_2d'):
                        omin_x, omin_y, omax_x, omax_y = obj.bbox_2d
                        if (omin_x <= x <= omax_x) and (omin_y <= y <= omax_y):
                            z_min1, z_max1 = map_object.source_bbox_3d[2], map_object.source_bbox_3d[5]
                            z_min2, z_max2 = obj.source_bbox_3d[2], obj.source_bbox_3d[5]
                            if not (z_max1 <= z_min2 or z_min1 >= z_max2):
                                return True
    return False

def update_grid_map_incremental(map_rep: MapRepresentation, map_object: MapObject, resolution: float = 1.0):
    """
    增量更新grid map，只添加新物体的障碍区域。
    """
    if map_rep.grid_map is None:
        # 没有grid map，先全量生成
        map_rep.grid_map = generate_grid_map_from_objects(map_rep, resolution)
        return
    min_x, min_y, max_x, max_y = map_object.bbox_2d
    grid_w, grid_h = map_rep.grid_map.shape
    for i in range(grid_w):
        for j in range(grid_h):
            x = (i + 0.5) * resolution
            y = (j + 0.5) * resolution
            if (min_x <= x <= max_x) and (min_y <= y <= max_y):
                map_rep.grid_map[i, j] = 0

def update_grid_map_full(map_rep: MapRepresentation, resolution: float = 1.0):
    """
    全量更新grid map，遍历所有物体。
    """
    map_rep.grid_map = generate_grid_map_from_objects(map_rep, resolution)

def add_object_with_collision_check(map_rep: MapRepresentation, map_object: MapObject, resolution: float = 1.0, new_position: Tuple[float, float, float] = None):
    """
    添加物体前做碰撞检测，支持指定新位置，成功后增量更新grid map。
    """
    if new_position is not None:
        map_object.position = new_position
        x, y, z = new_position
        w, d, h = map_object.size
        map_object.source_bbox_3d = (
            x, y, z,
            x + w, y + d, z + h
        )
        map_object.source_centroid_3d = (x + w/2, y + d/2, z + h/2)
        map_object.bbox_2d = (x, y, x + w, y + d)
    if check_collision_with_grid(map_rep, map_object, resolution):
        raise ValueError("物体与现有物体发生不可叠加的碰撞，添加失败！")
    map_rep.objects[map_object.object_id] = map_object
    update_grid_map_incremental(map_rep, map_object, resolution)
