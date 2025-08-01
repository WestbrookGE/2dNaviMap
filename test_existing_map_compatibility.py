#!/usr/bin/env python3
"""
测试PNG存储与现有地图的兼容性
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

def test_existing_map_compatibility():
    """测试与现有地图的兼容性"""
    print("=== 测试PNG存储与现有地图的兼容性 ===")
    
    # 1. 加载现有地图
    print("\n1. 加载现有地图...")
    try:
        map_rep = MapRepresentation.load_from_json("data/maps/complete_indoor_scene.json")
        print(f"成功加载地图: {map_rep.map_id}")
        print(f"物体数量: {len(map_rep.objects)}")
        print(f"画布大小: {map_rep.canvas_size}")
        
        # 检查是否已有grid_map
        if map_rep.grid_map is not None:
            print(f"现有grid_map形状: {map_rep.grid_map.shape}")
        else:
            print("现有地图没有grid_map，将生成新的")
    except Exception as e:
        print(f"加载现有地图失败: {e}")
        return
    
    # 2. 生成新的grid_map（使用0.01精度）
    print("\n2. 生成新的grid_map...")
    print(f"使用精度: {config.get_default_resolution()} 米")
    
    grid_map = generate_grid_map_from_objects(map_rep)
    map_rep.grid_map = grid_map
    
    print(f"新grid_map形状: {grid_map.shape}")
    print(f"障碍物像素数量: {np.sum(grid_map == 0)}")
    print(f"可通行像素数量: {np.sum(grid_map == 1)}")
    
    # 3. 保存为PNG
    print("\n3. 保存为PNG...")
    png_path = map_rep.save_grid_map_as_png()
    if png_path:
        print(f"PNG文件已保存: {png_path}")
        print(f"文件大小: {os.path.getsize(png_path)} 字节")
    else:
        print("保存PNG文件失败")
    
    # 4. 测试从PNG重新加载
    print("\n4. 测试从PNG重新加载...")
    
    # 创建新的地图对象（模拟重新加载）
    new_map_rep = MapRepresentation.load_from_json("data/maps/complete_indoor_scene.json")
    
    # 从PNG加载grid_map
    success = new_map_rep.load_grid_map_from_png()
    if success and new_map_rep.grid_map is not None:
        print("成功从PNG加载grid_map")
        print(f"加载的grid_map形状: {new_map_rep.grid_map.shape}")
        
        # 验证数据一致性
        if np.array_equal(map_rep.grid_map, new_map_rep.grid_map):
            print("✓ 数据一致性验证通过")
        else:
            print("✗ 数据一致性验证失败")
    else:
        print("从PNG加载grid_map失败")
    
    # 5. 可视化对比
    print("\n5. 可视化对比...")
    plt.figure(figsize=(15, 10))
    
    # 显示原始地图
    plt.subplot(2, 2, 1)
    plot_map(map_rep, show_grid=True, show_legend=False, figsize=(7, 5))
    plt.title("原始地图（内存中的grid_map）")
    
    # 显示从PNG加载的地图
    plt.subplot(2, 2, 2)
    plot_map(new_map_rep, show_grid=True, show_legend=False, figsize=(7, 5))
    plt.title("从PNG加载的地图")
    
    # 显示grid_map的细节
    plt.subplot(2, 2, 3)
    if map_rep.grid_map is not None:
        plt.imshow(map_rep.grid_map, cmap='gray', origin='lower')
        plt.title("Grid Map（内存）")
        plt.colorbar()
    
    plt.subplot(2, 2, 4)
    if new_map_rep.grid_map is not None:
        plt.imshow(new_map_rep.grid_map, cmap='gray', origin='lower')
        plt.title("Grid Map（从PNG加载）")
        plt.colorbar()
    
    plt.tight_layout()
    plt.savefig("existing_map_compatibility_test.png", dpi=150, bbox_inches='tight')
    print("可视化结果已保存为: existing_map_compatibility_test.png")
    
    # 6. 性能测试
    print("\n6. 性能测试...")
    import time
    
    # 测试PNG保存性能
    start_time = time.time()
    for i in range(5):
        png_path = map_rep.save_grid_map_as_png()
    save_time = (time.time() - start_time) / 5
    print(f"PNG保存平均时间: {save_time:.4f} 秒")
    
    # 测试PNG加载性能
    start_time = time.time()
    for i in range(5):
        success = new_map_rep.load_grid_map_from_png()
    load_time = (time.time() - start_time) / 5
    print(f"PNG加载平均时间: {load_time:.4f} 秒")
    
    # 7. 文件大小对比
    print("\n7. 文件大小对比...")
    if png_path and os.path.exists(png_path):
        png_size = os.path.getsize(png_path)
        print(f"PNG文件大小: {png_size} 字节")
        
        # 估算numpy数组大小
        if map_rep.grid_map is not None:
            array_size = map_rep.grid_map.nbytes
            print(f"Numpy数组大小: {array_size} 字节")
            compression_ratio = array_size / png_size
            print(f"压缩比: {compression_ratio:.2f}x")
    
    print("\n=== 兼容性测试完成 ===")

if __name__ == "__main__":
    test_existing_map_compatibility() 