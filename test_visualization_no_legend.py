#!/usr/bin/env python3
"""
测试无图例的可视化效果
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

def test_visualization_no_legend():
    """测试无图例的可视化效果"""
    print("=== 测试无图例的可视化效果 ===")
    
    # 1. 创建测试地图
    print("\n1. 创建测试地图...")
    map_rep = MapRepresentation(
        map_id="legend_test",
        source_type=SourceType.OTHER,
        objects={},
        grid_map=None,
        scene_description="图例测试地图",
        canvas_size=(8.0, 6.0),  # 8m x 6m
    )
    
    # 2. 添加多个不同类型的物体
    print("\n2. 添加测试物体...")
    
    # 添加墙体
    wall1 = MapObject(
        label="wall",
        size=(0.2, 2.0, 2.5),
        position=(1.0, 1.0, 0.0),
        id="wall_1"
    )
    map_rep.objects["wall_1"] = wall1
    
    wall2 = MapObject(
        label="wall",
        size=(0.2, 2.0, 2.5),
        position=(3.0, 2.0, 0.0),
        id="wall_2"
    )
    map_rep.objects["wall_2"] = wall2
    
    # 添加门
    door1 = MapObject(
        label="door",
        size=(0.1, 0.8, 2.0),
        position=(2.0, 0.5, 0.0),
        id="door_1"
    )
    map_rep.objects["door_1"] = door1
    
    # 添加家具
    table1 = MapObject(
        label="table",
        size=(1.2, 0.8, 0.75),
        position=(0.5, 3.0, 0.0),
        id="table_1"
    )
    map_rep.objects["table_1"] = table1
    
    chair1 = MapObject(
        label="chair",
        size=(0.5, 0.5, 0.9),
        position=(1.0, 4.0, 0.0),
        id="chair_1"
    )
    map_rep.objects["chair_1"] = chair1
    
    sofa1 = MapObject(
        label="sofa",
        size=(2.0, 0.8, 0.8),
        position=(4.0, 4.0, 0.0),
        id="sofa_1"
    )
    map_rep.objects["sofa_1"] = sofa1
    
    # 3. 生成grid_map
    print("\n3. 生成grid_map...")
    grid_map = generate_grid_map_from_objects(map_rep)
    map_rep.grid_map = grid_map
    
    print(f"Grid map形状: {grid_map.shape}")
    print(f"障碍物像素数量: {np.sum(grid_map == 0)}")
    print(f"可通行像素数量: {np.sum(grid_map == 1)}")
    
    # 4. 可视化对比
    print("\n4. 可视化对比...")
    plt.figure(figsize=(16, 8))
    
    # 显示地图（无图例）
    plt.subplot(1, 3, 1)
    plot_map(map_rep, show_grid=True, show_legend=False, figsize=(6, 4))
    plt.title("无图例显示")
    
    # 显示地图（有图例）
    plt.subplot(1, 3, 2)
    plot_map(map_rep, show_grid=True, show_legend=True, figsize=(6, 4))
    plt.title("有图例显示")
    
    # 显示地图（无网格，无图例）
    plt.subplot(1, 3, 3)
    plot_map(map_rep, show_grid=False, show_legend=False, figsize=(6, 4))
    plt.title("无网格，无图例")
    
    plt.tight_layout()
    plt.savefig("visualization_legend_comparison.png", dpi=150, bbox_inches='tight')
    print("可视化对比结果已保存为: visualization_legend_comparison.png")
    
    # 5. 显示物体信息
    print("\n5. 物体信息:")
    for obj_id, obj in map_rep.objects.items():
        print(f"  {obj_id}: {obj.label} at {obj.position}, size {obj.size}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_visualization_no_legend() 