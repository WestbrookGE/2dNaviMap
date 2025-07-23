import numpy as np
from core.data_structures import MapRepresentation
from typing import Tuple

def generate_grid_map_from_objects(map_rep: MapRepresentation, resolution: float = 1.0) -> np.ndarray:
    """
    根据地图物体自动生成可通行grid map。
    障碍物区域为0，可通行区域为1。
    :param map_rep: MapRepresentation对象
    :param resolution: 每个grid的实际长度
    :return: grid map (numpy array)
    """
    if map_rep.canvas_size is None:
        raise ValueError("Map canvas_size未设置，无法生成grid map")
    width, height = map_rep.canvas_size
    grid_w = int(np.ceil(width / resolution))
    grid_h = int(np.ceil(height / resolution))
    grid_map = np.ones((grid_w, grid_h), dtype=np.uint8)
    # 用2D bbox判断障碍
    for obj in map_rep.objects.values():
        if hasattr(obj, 'bbox_2d'):
            min_x, min_y, max_x, max_y = obj.bbox_2d
            for i in range(grid_w):
                for j in range(grid_h):
                    x = (i + 0.5) * resolution
                    y = (j + 0.5) * resolution
                    if (min_x <= x <= max_x) and (min_y <= y <= max_y):
                        grid_map[i, j] = 0
    return grid_map
