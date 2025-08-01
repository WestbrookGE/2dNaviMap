#!/usr/bin/env python3
"""
测试地图生成功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_structures import MapRepresentation, MapObject, SourceType
from utils.config import config
from processors.geometry_processor import generate_grid_map_from_objects
from utils.visualization import plot_map
import matplotlib.pyplot as plt
import numpy as np

def test_simple_map_generation():
    """测试简单地图生成"""
    print("=== 测试简单地图生成 ===")
    
    # 1. 创建简单地图
    print("\n1. 创建简单地图...")
    map_rep = MapRepresentation(
        map_id="simple_test",
        source_type=SourceType.OTHER,
        objects={},
        grid_map=None,
        scene_description="简单测试地图",
        canvas_size=(5.0, 5.0),  # 5m x 5m
    )
    
    # 2. 添加一个简单的墙体
    print("\n2. 添加墙体...")
    wall = MapObject(
        label="wall",
        size=(0.2, 2.0, 2.5),  # 厚度0.2m，长度2m，高度2.5m
        position=(1.0, 1.0, 0.0),
        id="wall_1"
    )
    map_rep.objects["wall_1"] = wall
    
    print(f"墙体位置: {wall.position}")
    print(f"墙体大小: {wall.size}")
    print(f"墙体2D边界框: {wall.get_bbox_2d()}")
    
    # 3. 生成grid_map
    print("\n3. 生成grid_map...")
    print(f"精度: {config.get_default_resolution()} 米")
    print(f"画布大小: {map_rep.canvas_size} 米")
    
    grid_map = generate_grid_map_from_objects(map_rep)
    map_rep.grid_map = grid_map
    
    print(f"Grid map形状: {grid_map.shape}")
    print(f"障碍物像素数量: {np.sum(grid_map == 0)}")
    print(f"可通行像素数量: {np.sum(grid_map == 1)}")
    
    # 4. 可视化
    print("\n4. 可视化地图...")
    plt.figure(figsize=(10, 8))
    
    # 显示地图（不显示图例）
    plt.subplot(1, 2, 1)
    plot_map(map_rep, show_grid=True, show_legend=False, figsize=(6, 4))
    plt.title("地图（无图例）")
    
    # 显示地图（显示图例）
    plt.subplot(1, 2, 2)
    plot_map(map_rep, show_grid=True, show_legend=True, figsize=(6, 4))
    plt.title("地图（有图例）")
    
    plt.tight_layout()
    plt.savefig("test_map_generation.png", dpi=150, bbox_inches='tight')
    print("可视化结果已保存为: test_map_generation.png")
    
    # 5. 检查grid_map的详细信息
    print("\n5. Grid map详细信息...")
    print(f"Grid map类型: {type(grid_map)}")
    print(f"Grid map数据类型: {grid_map.dtype}")
    print(f"Grid map最小值: {np.min(grid_map)}")
    print(f"Grid map最大值: {np.max(grid_map)}")
    print(f"Grid map唯一值: {np.unique(grid_map)}")
    
    # 检查墙体区域的grid_map值
    min_x, min_y, max_x, max_y = wall.get_bbox_2d()
    print(f"墙体区域: x=[{min_x:.2f}, {max_x:.2f}], y=[{min_y:.2f}, {max_y:.2f}]")
    
    # 计算墙体在grid中的位置
    resolution = config.get_default_resolution()
    grid_w = int(round(map_rep.canvas_size[0] / resolution))
    grid_h = int(round(map_rep.canvas_size[1] / resolution))
    
    wall_min_col = int(min_x / resolution)
    wall_max_col = int(max_x / resolution)
    wall_min_row = int(min_y / resolution)
    wall_max_row = int(max_y / resolution)
    
    print(f"墙体在grid中的位置: 列[{wall_min_col}, {wall_max_col}], 行[{wall_min_row}, {wall_max_row}]")
    
    # 检查墙体区域的grid_map值
    wall_region = grid_map[wall_min_row:wall_max_row, wall_min_col:wall_max_col]
    print(f"墙体区域grid_map形状: {wall_region.shape}")
    print(f"墙体区域中0的数量: {np.sum(wall_region == 0)}")
    print(f"墙体区域中1的数量: {np.sum(wall_region == 1)}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_simple_map_generation() 