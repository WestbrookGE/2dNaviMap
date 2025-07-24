import matplotlib.pyplot as plt
import numpy as np
from core.data_structures import MapRepresentation, AgentState
import json
import os
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']  # 任选其一，自动匹配

def plot_map(map_rep: MapRepresentation, agent_state: AgentState = None, show_grid: bool = True, figsize=(8, 8), save_path: str = None):
    """
    绘制地图、物体轮廓、机器人位置与朝向。
    """
    fig, ax = plt.subplots(figsize=figsize)

    # 1. 绘制栅格地图
    if map_rep.grid_map is not None and show_grid:
        grid = map_rep.grid_map
        ax.imshow(
            grid,  # 不再转置
            origin='lower',
            cmap='Greys',
            alpha=0.3,
            extent=[0, map_rep.canvas_size[0], 0, map_rep.canvas_size[1]],
            interpolation='nearest',
            aspect='auto'  # 保证拉伸到整个画布
        )
        ax.set_xlim(0, map_rep.canvas_size[0])
        ax.set_ylim(0, map_rep.canvas_size[1])
    else:
        if hasattr(map_rep, "canvas_size") and map_rep.canvas_size is not None:
            ax.set_xlim(0, map_rep.canvas_size[0])
            ax.set_ylim(0, map_rep.canvas_size[1])

    # ====== 辅助点：画出左下角和右上角，调试坐标系 ======
    ax.plot(0, 0, 'ro', label='origin (0,0)')
    ax.plot(map_rep.canvas_size[0], map_rep.canvas_size[1], 'go', label='max')
    # =============================================

    # 2. 绘制所有物体的2D bbox
    for obj in map_rep.objects.values():
        if getattr(obj, 'category', None) == 'path' and hasattr(obj, 'footprint_2d'):
            # 绘制轨迹线
            pts = np.array(obj.footprint_2d)
            if len(pts) > 1:
                ax.plot(pts[:,0], pts[:,1], '-o', label=obj.category+":"+obj.object_id)
        elif hasattr(obj, 'bbox_2d'):
            min_x, min_y, max_x, max_y = obj.bbox_2d
            rect = plt.Rectangle((min_x, min_y), max_x - min_x, max_y - min_y, alpha=0.4, label=obj.category+":"+obj.object_id)
            ax.add_patch(rect)
            centroid = ((min_x + max_x) / 2, (min_y + max_y) / 2)
            ax.text(centroid[0], centroid[1], obj.category, fontsize=8, ha='center', va='center')

    # 3. 绘制机器人本体
    if agent_state is not None and hasattr(agent_state, 'bbox_2d'):
        min_x, min_y, max_x, max_y = agent_state.bbox_2d
        rect = plt.Rectangle((min_x, min_y), max_x - min_x, max_y - min_y, color='blue', alpha=0.5, label='Agent')
        ax.add_patch(rect)
        centroid = ((min_x + max_x) / 2, (min_y + max_y) / 2)
        ax.plot(centroid[0], centroid[1], 'ro', markersize=8)
        dx = 0.5 * np.cos(agent_state.orientation)
        dy = 0.5 * np.sin(agent_state.orientation)
        ax.arrow(centroid[0], centroid[1], dx, dy, head_width=0.2, head_length=0.2, fc='r', ec='r')
        ax.text(centroid[0], centroid[1], 'Agent', fontsize=10, color='blue', ha='left', va='bottom')

    ax.set_aspect('equal')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title(f"Map: {map_rep.map_id}")
    ax.legend(fontsize=7, loc='best')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()


def plot_from_json(map_json_path: str, agent_json_path: str = None, **kwargs):
    """
    从json文件加载MapRepresentation和AgentState并绘制
    """
    map_rep = MapRepresentation.load_from_json(map_json_path)
    agent_state = AgentState.load_from_json(agent_json_path) if agent_json_path else None
    plot_map(map_rep, agent_state, **kwargs)
