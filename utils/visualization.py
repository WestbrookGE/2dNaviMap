import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple
from core.data_structures import MapRepresentation, AgentState
from utils.config import config
import json
import os
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']  # 任选其一，自动匹配

def expand_bbox_for_collision(bbox_2d: Tuple[float, float, float, float], 
                             collision_margin: float = None) -> Tuple[float, float, float, float]:
    """
    为物体的2D边界框添加碰撞边缘
    :param bbox_2d: 原始边界框 (min_x, min_y, max_x, max_y)
    :param collision_margin: 碰撞边缘距离，如果为None则使用配置值
    :return: 扩展后的边界框
    """
    if collision_margin is None:
        collision_margin = config.get_collision_margin()
    
    if collision_margin <= 0:
        return bbox_2d
    
    min_x, min_y, max_x, max_y = bbox_2d
    return (min_x - collision_margin, min_y - collision_margin, 
            max_x + collision_margin, max_y + collision_margin)

def plot_map(map_rep: MapRepresentation, agent_state: AgentState = None, show_grid: bool = True, 
             figsize=(8, 8), save_path: str = None, show_collision_margin: bool = True):
    """
    绘制地图、物体轮廓、机器人位置与朝向。
    :param show_collision_margin: 是否显示碰撞边缘
    """
    fig, ax = plt.subplots(figsize=figsize)

    # 1. 绘制栅格地图
    if map_rep.grid_map is not None and show_grid:
        grid = map_rep.grid_map
        ax.imshow(
            grid,  # 不再转置
            origin='lower',
            cmap='Greys',
            alpha=config.get_visualization_alpha(),
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

    # 2. 绘制所有物体的2D bbox
    for obj in map_rep.objects.values():
        if getattr(obj, 'label', None) == 'path' and hasattr(obj, 'footprint_2d'):
            # 绘制轨迹线
            pts = np.array(obj.footprint_2d)
            if len(pts) > 1:
                ax.plot(pts[:,0], pts[:,1], '-o', label=obj.label+":"+obj.id)
        elif hasattr(obj, 'bbox_2d'):
            min_x, min_y, max_x, max_y = obj.bbox_2d
            
            # 根据物体类型设置不同的颜色和样式
            if obj.label == "wall":
                # 墙体：深灰色，实线边框
                rect = plt.Rectangle((min_x, min_y), max_x - min_x, max_y - min_y, 
                                   facecolor='darkgray', edgecolor='black', 
                                   linewidth=2, alpha=0.8, label=obj.label+":"+obj.id)
            elif obj.label == "door":
                # 门：棕色，虚线边框
                rect = plt.Rectangle((min_x, min_y), max_x - min_x, max_y - min_y, 
                                   facecolor='brown', edgecolor='darkred', 
                                   linewidth=2, linestyle='--', alpha=0.7, label=obj.label+":"+obj.id)
            else:
                # 家具：浅色，细边框
                rect = plt.Rectangle((min_x, min_y), max_x - min_x, max_y - min_y, 
                                   facecolor='lightblue', edgecolor='blue', 
                                   linewidth=1, alpha=0.4, label=obj.label+":"+obj.id)
            
            ax.add_patch(rect)
            centroid = ((min_x + max_x) / 2, (min_y + max_y) / 2)
            
            # 根据物体类型设置不同的文字颜色
            if obj.label == "wall":
                text_color = 'white'
                fontweight = 'bold'
            elif obj.label == "door":
                text_color = 'white'
                fontweight = 'bold'
            else:
                text_color = 'black'
                fontweight = 'normal'
            
            ax.text(centroid[0], centroid[1], obj.label, fontsize=8, 
                   ha='center', va='center', color=text_color, fontweight=fontweight)
            
            # 绘制碰撞边缘
            if show_collision_margin:
                collision_bbox = expand_bbox_for_collision(obj.bbox_2d)
                c_min_x, c_min_y, c_max_x, c_max_y = collision_bbox
                
                # 碰撞边缘：红色虚线边框，半透明
                collision_rect = plt.Rectangle((c_min_x, c_min_y), 
                                             c_max_x - c_min_x, c_max_y - c_min_y,
                                             facecolor='none', edgecolor='red', 
                                             linewidth=1, linestyle='--', alpha=0.6)
                ax.add_patch(collision_rect)

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
        
        # 绘制机器人的碰撞边缘
        if show_collision_margin:
            collision_bbox = expand_bbox_for_collision(agent_state.bbox_2d)
            c_min_x, c_min_y, c_max_x, c_max_y = collision_bbox
            
            # 机器人的碰撞边缘：蓝色虚线边框
            collision_rect = plt.Rectangle((c_min_x, c_min_y), 
                                         c_max_x - c_min_x, c_max_y - c_min_y,
                                         facecolor='none', edgecolor='blue', 
                                         linewidth=1, linestyle='--', alpha=0.8)
            ax.add_patch(collision_rect)

    ax.set_aspect('equal')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    title = f"Map: {map_rep.map_id}"
    if show_collision_margin:
        title += f" (碰撞边缘: {config.get_collision_margin()}m)"
    ax.set_title(title)
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
