import heapq
from typing import List, Tuple, Optional
import numpy as np
from core.data_structures import Path
from utils.config import config

def expand_obstacles(grid_map: np.ndarray, resolution: float, collision_margin: float = None) -> np.ndarray:
    """
    扩展障碍物，为每个障碍物增加碰撞体积
    :param grid_map: 原始网格地图，0为障碍，1为可通行
    :param resolution: 网格分辨率（米/格子）
    :param collision_margin: 碰撞体积扩展距离（米），如果为None则使用配置值
    :return: 扩展后的网格地图
    """
    if collision_margin is None:
        collision_margin = config.get_collision_margin()
    
    if collision_margin <= 0:
        return grid_map.copy()
    
    # 计算需要扩展的格子数
    expand_cells = int(np.ceil(collision_margin / resolution))
    
    # 创建扩展后的地图
    expanded_map = grid_map.copy()
    height, width = grid_map.shape
    
    # 找到所有障碍物位置
    obstacle_positions = np.where(grid_map == 0)
    
    # 为每个障碍物扩展碰撞体积
    for row, col in zip(obstacle_positions[0], obstacle_positions[1]):
        # 计算扩展范围
        min_row = max(0, row - expand_cells)
        max_row = min(height - 1, row + expand_cells)
        min_col = max(0, col - expand_cells)
        max_col = min(width - 1, col + expand_cells)
        
        # 将扩展范围内的格子标记为障碍物
        expanded_map[min_row:max_row+1, min_col:max_col+1] = 0
    
    return expanded_map

def find_nearest_free_position(grid_map: np.ndarray, target_pos: Tuple[float, float], 
                             resolution: float, max_search_radius: float = None) -> Optional[Tuple[float, float]]:
    """
    找到距离目标位置最近的可行位置
    :param grid_map: 网格地图，0为障碍，1为可通行
    :param target_pos: 目标位置 (x, y)
    :param resolution: 网格分辨率
    :param max_search_radius: 最大搜索半径（米），如果为None则使用配置值
    :return: 最近的可行位置，如果找不到则返回None
    """
    if max_search_radius is None:
        max_search_radius = config.get_max_search_radius()
    
    def to_grid(pos):
        x, y = pos
        col = int(x // resolution)
        row = int(y // resolution)
        return row, col

    def to_world(row, col):
        x = (col + 0.5) * resolution
        y = (row + 0.5) * resolution
        return x, y

    grid_h, grid_w = grid_map.shape
    target_grid = to_grid(target_pos)
    
    # 如果目标位置本身就是可行的，直接返回
    if (0 <= target_grid[0] < grid_h and 0 <= target_grid[1] < grid_w and 
        grid_map[target_grid[0], target_grid[1]] == 1):
        return target_pos
    
    # 计算搜索范围（格子数）
    search_cells = int(max_search_radius / resolution)
    
    # 在目标位置周围搜索最近的可行位置
    min_row = max(0, target_grid[0] - search_cells)
    max_row = min(grid_h - 1, target_grid[0] + search_cells)
    min_col = max(0, target_grid[1] - search_cells)
    max_col = min(grid_w - 1, target_grid[1] + search_cells)
    
    best_pos = None
    best_distance = float('inf')
    
    for row in range(min_row, max_row + 1):
        for col in range(min_col, max_col + 1):
            if grid_map[row, col] == 1:  # 可行位置
                world_pos = to_world(row, col)
                distance = np.linalg.norm(np.array(world_pos) - np.array(target_pos))
                if distance < best_distance:
                    best_distance = distance
                    best_pos = world_pos
    
    return best_pos

def astar_search(grid_map: np.ndarray, start: Tuple[float, float], goal: Tuple[float, float], 
                 resolution: float = None, collision_margin: float = None) -> Optional[Path]:
    """
    A*寻路算法，返回Path对象。
    :param grid_map: numpy数组，0为障碍，1为可通行
    :param start: (x, y) 起点坐标（米）
    :param goal: (x, y) 终点坐标（米）
    :param resolution: 每个格子的实际长度，如果为None则使用配置值
    :param collision_margin: 碰撞体积扩展距离（米），如果为None则使用配置值
    :return: Path对象，若无路则返回None
    """
    if resolution is None:
        resolution = config.get_default_resolution()
    if collision_margin is None:
        collision_margin = config.get_collision_margin()
    
    # 扩展障碍物以添加碰撞体积
    expanded_map = expand_obstacles(grid_map, resolution, collision_margin)
    
    def to_grid(pos):
        x, y = pos
        col = int(x // resolution)
        row = int(y // resolution)
        return row, col

    def to_world(row, col):
        x = (col + 0.5) * resolution
        y = (row + 0.5) * resolution
        return x, y

    # 找到可行的起点和终点
    feasible_start = find_nearest_free_position(expanded_map, start, resolution)
    feasible_goal = find_nearest_free_position(expanded_map, goal, resolution)
    
    if feasible_start is None or feasible_goal is None:
        print(f"警告: 无法找到可行的起点或终点")
        print(f"原始起点: {start}, 原始终点: {goal}")
        return None
    
    # 如果起点或终点被调整，打印信息
    if feasible_start != start:
        print(f"起点从 {start} 调整到 {feasible_start}")
    if feasible_goal != goal:
        print(f"终点从 {goal} 调整到 {feasible_goal}")

    grid_h, grid_w = expanded_map.shape  # (行,列)=(y,x)
    start_idx = to_grid(feasible_start)
    goal_idx = to_grid(feasible_goal)
    
    # A*主循环
    open_set = []
    heapq.heappush(open_set, (0, start_idx))
    came_from = {}
    g_score = {start_idx: 0}
    f_score = {start_idx: np.linalg.norm(np.array(start_idx) - np.array(goal_idx))}
    dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal_idx:
            # 回溯路径
            path = []
            while current in came_from:
                pt = to_world(*current)
                pt = (round(pt[0], 1), round(pt[1], 1))
                path.append(pt)
                current = came_from[current]
            pt = to_world(*start_idx)
            pt = (round(pt[0], 1), round(pt[1], 1))
            path.append(pt)
            path.reverse()
            sampled_path = sample_path(path, step=0.5)
            return Path(points=sampled_path)
        for d_row, d_col in dirs:
            neighbor = (current[0] + d_row, current[1] + d_col)
            if not (0 <= neighbor[0] < grid_h and 0 <= neighbor[1] < grid_w):
                continue
            if expanded_map[neighbor[0], neighbor[1]] == 0:
                continue
            tentative_g = g_score[current] + np.linalg.norm(np.array(neighbor) - np.array(current))
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + np.linalg.norm(np.array(neighbor) - np.array(goal_idx))
                f_score[neighbor] = f
                heapq.heappush(open_set, (f, neighbor))
    return None

def sample_path(points, step=0.5):
    if not points or len(points) < 2:
        return points
    sampled = [points[0]]
    acc = 0.0
    for i in range(1, len(points)):
        x0, y0 = sampled[-1]
        x1, y1 = points[i]
        dx, dy = x1 - x0, y1 - y0
        dist = (dx**2 + dy**2) ** 0.5
        while acc + dist >= step:
            ratio = (step - acc) / dist
            nx = x0 + ratio * dx
            ny = y0 + ratio * dy
            sampled.append((round(nx, 1), round(ny, 1)))
            x0, y0 = nx, ny
            dx, dy = x1 - x0, y1 - y0
            dist = (dx**2 + dy**2) ** 0.5
            acc = 0.0
        acc += dist
    if sampled[-1] != points[-1]:
        sampled.append((round(points[-1][0], 1), round(points[-1][1], 1)))
    return sampled
