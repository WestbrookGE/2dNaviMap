import heapq
from typing import List, Tuple, Optional
import numpy as np
from core.data_structures import Path

def astar_search(grid_map: np.ndarray, start: Tuple[float, float], goal: Tuple[float, float], resolution: float = 1.0) -> Optional[Path]:
    """
    A*寻路算法，返回Path对象。
    :param grid_map: numpy数组，0为障碍，1为可通行
    :param start: (x, y) 起点坐标（米）
    :param goal: (x, y) 终点坐标（米）
    :param resolution: 每个格子的实际长度
    :return: Path对象，若无路则返回None
    """
    def to_grid(pos):
        x, y = pos
        col = int(x // resolution)
        row = int(y // resolution)
        return row, col

    def to_world(row, col):
        x = (col + 0.5) * resolution
        y = (row + 0.5) * resolution
        return x, y

    grid_h, grid_w = grid_map.shape  # (行,列)=(y,x)
    start_idx = to_grid(start)
    goal_idx = to_grid(goal)
    if not (0 <= start_idx[0] < grid_h and 0 <= start_idx[1] < grid_w):
        return None
    if not (0 <= goal_idx[0] < grid_h and 0 <= goal_idx[1] < grid_w):
        return None
    if grid_map[start_idx[0], start_idx[1]] == 0 or grid_map[goal_idx[0], goal_idx[1]] == 0:
        return None

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
            if grid_map[neighbor[0], neighbor[1]] == 0:
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
