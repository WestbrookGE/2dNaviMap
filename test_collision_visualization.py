#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试碰撞边缘可视化效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.visualization import plot_map, plot_from_json
from core.data_structures import MapRepresentation, MapObject, SourceType
from utils.config import config
import numpy as np

def create_test_map():
    """创建一个测试地图，包含不同类型的物体"""
    objects = {}
    
    # 添加墙体
    wall1 = MapObject("wall", (2.0, 0.2, 2.0), (1.0, 1.0, 0.0), "wall_1")
    wall2 = MapObject("wall", (0.2, 3.0, 2.0), (5.0, 2.0, 0.0), "wall_2")
    objects["wall_1"] = wall1
    objects["wall_2"] = wall2
    
    # 添加门
    door1 = MapObject("door", (0.8, 0.1, 2.0), (3.0, 4.0, 0.0), "door_1")
    objects["door_1"] = door1
    
    # 添加家具
    chair1 = MapObject("chair", (0.5, 0.5, 0.8), (2.0, 3.0, 0.0), "chair_1")
    table1 = MapObject("table", (1.2, 0.8, 0.7), (4.0, 1.5, 0.0), "table_1")
    sofa1 = MapObject("sofa", (2.0, 0.8, 0.8), (6.0, 3.0, 0.0), "sofa_1")
    objects["chair_1"] = chair1
    objects["table_1"] = table1
    objects["sofa_1"] = sofa1
    
    # 创建地图表示
    map_rep = MapRepresentation(
        map_id="test_collision_map",
        source_type=SourceType.OTHER,
        objects=objects,
        canvas_size=(10.0, 8.0)
    )
    
    return map_rep

def test_collision_visualization():
    """测试碰撞边缘可视化"""
    print("创建测试地图...")
    map_rep = create_test_map()
    
    print(f"碰撞边缘距离: {config.get_collision_margin()}m")
    print("绘制地图（显示碰撞边缘）...")
    
    # 绘制带碰撞边缘的地图
    plot_map(map_rep, show_collision_margin=True, show_legend=False, figsize=(12, 10))
    
    print("绘制地图（不显示碰撞边缘）...")
    
    # 绘制不带碰撞边缘的地图作为对比
    plot_map(map_rep, show_collision_margin=False, show_legend=False, figsize=(12, 10))

def test_with_json_map():
    """使用JSON地图文件测试"""
    # 检查是否有可用的地图文件
    map_files = [
        "data/maps/complete_indoor_scene.json",
        "data/map_demo.json"
    ]
    
    for map_file in map_files:
        if os.path.exists(map_file):
            try:
                print(f"使用地图文件: {map_file}")
                plot_from_json(map_file, show_collision_margin=True, figsize=(12, 10))
                return
            except Exception as e:
                print(f"加载地图文件 {map_file} 失败: {e}")
                continue
    
    print("未找到可用的地图文件，使用测试地图")

if __name__ == "__main__":
    print("=== 碰撞边缘可视化测试 ===")
    
    # 测试1: 使用测试地图
    test_collision_visualization()
    
    # 测试2: 使用JSON地图文件
    print("\n=== 使用JSON地图文件测试 ===")
    test_with_json_map() 