#!/usr/bin/env python3
"""
测试现有地图的可视化
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_structures import MapRepresentation
from utils.config import config
from processors.geometry_processor import generate_grid_map_from_objects
from utils.visualization import plot_map
import matplotlib.pyplot as plt
import numpy as np

def test_existing_map_visualization():
    """测试现有地图的可视化"""
    print("=== 测试现有地图的可视化 ===")
    
    # 1. 加载现有地图
    print("\n1. 加载现有地图...")
    try:
        map_rep = MapRepresentation.load_from_json("data/maps/complete_indoor_scene.json")
        print(f"成功加载地图: {map_rep.map_id}")
        print(f"物体数量: {len(map_rep.objects)}")
        print(f"画布大小: {map_rep.canvas_size}")
        
        # 显示前几个物体的信息
        print("\n前5个物体:")
        for i, (obj_id, obj) in enumerate(map_rep.objects.items()):
            if i >= 5:
                break
            print(f"  {obj_id}: {obj.label} at {obj.position}, size {obj.size}")
        
    except Exception as e:
        print(f"加载现有地图失败: {e}")
        return
    
    # 2. 检查grid_map
    print("\n2. 检查grid_map...")
    if map_rep.grid_map is not None:
        print(f"现有grid_map形状: {map_rep.grid_map.shape}")
        print(f"障碍物像素数量: {np.sum(map_rep.grid_map == 0)}")
        print(f"可通行像素数量: {np.sum(map_rep.grid_map == 1)}")
    else:
        print("没有现有grid_map，将生成新的")
        grid_map = generate_grid_map_from_objects(map_rep)
        map_rep.grid_map = grid_map
        print(f"生成的新grid_map形状: {grid_map.shape}")
        print(f"障碍物像素数量: {np.sum(grid_map == 0)}")
        print(f"可通行像素数量: {np.sum(grid_map == 1)}")
    
    # 3. 可视化（不显示图例）
    print("\n3. 可视化地图（无图例）...")
    plt.figure(figsize=(12, 8))
    
    plt.subplot(1, 2, 1)
    plot_map(map_rep, show_grid=True, show_legend=False, figsize=(8, 6))
    plt.title("现有地图（无图例）")
    
    # 可视化（显示图例）
    plt.subplot(1, 2, 2)
    plot_map(map_rep, show_grid=True, show_legend=True, figsize=(8, 6))
    plt.title("现有地图（有图例）")
    
    plt.tight_layout()
    plt.savefig("existing_map_visualization.png", dpi=150, bbox_inches='tight')
    print("可视化结果已保存为: existing_map_visualization.png")
    
    # 4. 检查grid_map的详细信息
    print("\n4. Grid map详细信息...")
    if map_rep.grid_map is not None:
        print(f"Grid map类型: {type(map_rep.grid_map)}")
        print(f"Grid map数据类型: {map_rep.grid_map.dtype}")
        print(f"Grid map最小值: {np.min(map_rep.grid_map)}")
        print(f"Grid map最大值: {np.max(map_rep.grid_map)}")
        print(f"Grid map唯一值: {np.unique(map_rep.grid_map)}")
        
        # 检查是否有障碍物
        obstacle_count = np.sum(map_rep.grid_map == 0)
        free_count = np.sum(map_rep.grid_map == 1)
        total_count = map_rep.grid_map.size
        
        print(f"总像素数: {total_count}")
        print(f"障碍物像素数: {obstacle_count} ({obstacle_count/total_count*100:.2f}%)")
        print(f"可通行像素数: {free_count} ({free_count/total_count*100:.2f}%)")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_existing_map_visualization() 