#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的碰撞边缘可视化测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.visualization import plot_map
from core.data_structures import MapRepresentation, MapObject, SourceType
from utils.config import config

def create_simple_test_map():
    """创建一个简单的测试地图"""
    objects = {}
    
    # 添加几个不同位置的物体
    chair1 = MapObject("chair", (0.5, 0.5, 0.8), (2.0, 2.0, 0.0), "chair_1")
    table1 = MapObject("table", (1.2, 0.8, 0.7), (5.0, 3.0, 0.0), "table_1")
    wall1 = MapObject("wall", (0.2, 4.0, 2.0), (8.0, 1.0, 0.0), "wall_1")
    
    objects["chair_1"] = chair1
    objects["table_1"] = table1
    objects["wall_1"] = wall1
    
    map_rep = MapRepresentation(
        map_id="simple_collision_test",
        source_type=SourceType.OTHER,
        objects=objects,
        canvas_size=(10.0, 6.0)
    )
    
    return map_rep

def main():
    print("=== 碰撞边缘可视化演示 ===")
    print(f"当前碰撞边缘距离: {config.get_collision_margin()}m")
    
    map_rep = create_simple_test_map()
    
    print("\n1. 显示碰撞边缘（红色虚线）:")
    plot_map(map_rep, show_collision_margin=True, show_legend=False, figsize=(10, 8))
    
    print("\n2. 不显示碰撞边缘:")
    plot_map(map_rep, show_collision_margin=False, show_legend=False, figsize=(10, 8))
    
    print("\n演示完成！")
    print("说明:")
    print("- 实心矩形：物体的实际边界")
    print("- 红色虚线：碰撞边缘（与A*算法中的碰撞体积扩展一致）")
    print("- 碰撞边缘距离可通过config.yaml中的collision.margin配置")

if __name__ == "__main__":
    main() 