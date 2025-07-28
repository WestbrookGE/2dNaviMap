import numpy as np
from core.data_structures import MapRepresentation
from utils.config import config
from typing import Tuple

def generate_grid_map_from_objects(map_rep: MapRepresentation, resolution: float = None) -> np.ndarray:
    """
    根据地图物体自动生成可通行grid map。
    障碍物区域为0，可通行区域为1。
    :param map_rep: MapRepresentation对象
    :param resolution: 每个grid的实际长度，如果为None则使用配置值
    :return: grid map (numpy array)
    """
    if resolution is None:
        resolution = config.get_default_resolution()
    
    if map_rep.canvas_size is None:
        raise ValueError("Map canvas_size未设置，无法生成grid map")
    width, height = map_rep.canvas_size
    grid_w = int(round(width / resolution))
    grid_h = int(round(height / resolution))
    grid_map = np.ones((grid_h, grid_w), dtype=np.uint8)  # shape=(行,列)=(y,x)
    # 用2D bbox判断障碍
    for obj in map_rep.objects.values():
        if hasattr(obj, 'bbox_2d'):
            min_x, min_y, max_x, max_y = obj.bbox_2d
            for row in range(grid_h):  # y方向
                for col in range(grid_w):  # x方向
                    x = col * resolution  # 左下角
                    y = row * resolution
                    if (min_x <= x < max_x) and (min_y <= y < max_y):
                        grid_map[row, col] = 0  # row是y，col是x
    return grid_map
