from apis.interaction_api import create_map, add_object_from_file, update_grid_map_full, add_object_with_collision_check, add_wall, add_path, load_existing_map
from utils.visualization import plot_map
from core.data_structures import SourceType, Path, MapRepresentation
from utils.config import config
import os
from planners.astar import astar_search



# 选择模式：创建新地图 或 加载现有地图
USE_EXISTING_MAP = True  # 设置为True使用现有地图，False创建新地图

if USE_EXISTING_MAP:
    # 加载现有地图
    try:
        print("=== 加载地图: data/maps/complete_indoor_scene.json ===")
        map_rep = load_existing_map()
        print(f"✅ 地图加载成功!")
        print(f"地图信息:")
        print(f"- 地图ID: {map_rep.map_id}")
        print(f"- 画布大小: {map_rep.canvas_size}")
        print(f"- 物体数量: {len(map_rep.objects)}")
        print(f"- 栅格地图大小: {map_rep.grid_map.shape if map_rep.grid_map is not None else 'None'}")
        
        # 统计物体类型
        object_types = {}
        for obj in map_rep.objects.values():
            obj_type = obj.label
            object_types[obj_type] = object_types.get(obj_type, 0) + 1
        
        print(f"\n物体类型统计:")
        for obj_type, count in object_types.items():
            print(f"- {obj_type}: {count} 个")
            
    except Exception as e:
        print(f"❌ 加载地图失败: {e}")
        print("将创建新地图...")
        USE_EXISTING_MAP = False

if not USE_EXISTING_MAP:
    # 新建地图 - 使用配置文件中的参数
    canvas_size = config.get_default_canvas_size()
    resolution = config.get_grid_resolution()
    map_rep = create_map(map_id="complete_indoor_scene", canvas_size=canvas_size, source_type=SourceType.OTHER)
    update_grid_map_full(map_rep, resolution=resolution)

    # ========== 第一步：添加所有墙体 - 创建完整的房间布局 ===========
    print("=== 添加墙体 ===")

    # 外墙 - 完整的房间边界
    outer_walls = [
        ("wall_bottom", (15.0, 0.2, 2.5), (0.0, 0.0, 0.0)),      # 底部外墙
        ("wall_top", (15.0, 0.2, 2.5), (0.0, 11.8, 0.0)),         # 顶部外墙
        ("wall_left", (0.2, 12.0, 2.5), (0.0, 0.0, 0.0)),         # 左侧外墙
        ("wall_right", (0.2, 12.0, 2.5), (14.8, 0.0, 0.0)),       # 右侧外墙
    ]

    # 内墙 - 分隔房间，自然断开形成通道
    inner_walls = [
        # 分隔客厅和卧室的墙 - 在y=5.5处自然断开
        ("wall_living_bedroom_1", (0.2, 2.5, 2.5), (7.0, 3.0, 0.0)),  # 客厅-卧室分隔墙1（下方：3.0-5.5）
        ("wall_living_bedroom_2", (0.2, 3.5, 2.5), (7.0, 8.0, 0.0)),  # 客厅-卧室分隔墙2（上方：5.5-8.0）
        
        # 分隔客厅和厨房的墙 - 在y=1.5处自然断开
        ("wall_living_kitchen_1", (0.2, 1.5, 2.5), (7.0, 0.0, 0.0)),  # 客厅-厨房分隔墙1（下方：0.0-1.5）
        ("wall_living_kitchen_2", (0.2, 1.5, 2.5), (7.0, 3.0, 0.0)),  # 客厅-厨房分隔墙2（上方：1.5-3.0）
        
        # 分隔厨房和卫生间的墙 - 在y=1.5处自然断开
        ("wall_kitchen_bathroom_1", (0.2, 1.5, 2.5), (12.0, 0.0, 0.0)), # 厨房-卫生间分隔墙1（下方：0.0-1.5）
        ("wall_kitchen_bathroom_2", (0.2, 1.5, 2.5), (12.0, 3.0, 0.0)), # 厨房-卫生间分隔墙2（上方：1.5-3.0）
        
        # 分隔卧室和卫生间的墙 - 在y=5.5处自然断开
        ("wall_bedroom_bathroom_1", (0.2, 2.5, 2.5), (12.0, 3.0, 0.0)), # 卧室-卫生间分隔墙1（下方：3.0-5.5）
        ("wall_bedroom_bathroom_2", (0.2, 3.5, 2.5), (12.0, 8.0, 0.0)), # 卧室-卫生间分隔墙2（上方：5.5-8.0）
    ]

    # 添加外墙
    print("添加外墙...")
    for wall_id, wall_size, wall_pos in outer_walls:
        try:
            add_wall(map_rep, wall_id, wall_size, wall_pos, resolution=resolution)
            print(f"成功添加外墙: {wall_id}")
        except Exception as e:
            print(f"添加外墙 {wall_id} 失败: {e}")

    # 添加内墙
    print("添加内墙...")
    for wall_id, wall_size, wall_pos in inner_walls:
        try:
            add_wall(map_rep, wall_id, wall_size, wall_pos, resolution=resolution)
            print(f"成功添加内墙: {wall_id}")
        except Exception as e:
            print(f"添加内墙 {wall_id} 失败: {e}")

    # ========== 第二步：添加家具 ===========
    print("\n=== 添加家具 ===")

    # 客厅家具布局
    living_room_objects = {
        "sofa": (2.0, 8.0, 0.0),           # 沙发
        "coffee_table": (4.0, 7.5, 0.0),   # 咖啡桌
        "tv_stand": (6.0, 8.5, 0.0),       # 电视柜
        "floor_lamp": (1.5, 9.5, 0.0),     # 落地灯
        "plant": (5.0, 9.5, 0.0),          # 植物
        "chair": (3.5, 6.0, 0.0),          # 椅子
    }

    # 卧室家具布局
    bedroom_objects = {
        "bed": (9.0, 8.0, 0.0),            # 床
        "wardrobe": (13.0, 9.0, 0.0),      # 衣柜
        "vanity_table": (9.5, 6.0, 0.0),   # 梳妆台
        "lamp": (10.0, 7.0, 0.0),          # 台灯
        "mirror": (11.0, 6.0, 0.0),        # 镜子
        "chest_of_drawers": (12.0, 6.5, 0.0), # 抽屉柜
    }

    # 厨房家具布局
    kitchen_objects = {
        "fridge": (8.5, 1.5, 0.0),         # 冰箱
        "dining_table": (3.5, 2.5, 0.0),   # 餐桌
        "cabinet": (2.0, 0.5, 0.0),        # 橱柜
        "bar_cart": (6.0, 1.0, 0.0),       # 餐车
    }

    # 卫生间家具布局
    bathroom_objects = {
        "mirror": (13.5, 1.0, 0.0),        # 镜子
        "cabinet": (12.5, 0.5, 0.0),       # 柜子
        "trash_bin": (14.0, 0.5, 0.0),     # 垃圾桶
    }

    # 合并所有家具
    all_objects = {
        **living_room_objects,
        **bedroom_objects,
        **kitchen_objects,
        **bathroom_objects
    }

    # 添加家具到地图
    for obj_name, pos in all_objects.items():
        try:
            add_object_with_collision_check(map_rep, obj_name, new_position=pos, object_dir=os.path.join("data", "objects"), resolution=resolution)
            print(f"成功添加 {obj_name} 到位置 {pos}")
        except Exception as e:
            print(f"添加 {obj_name} 失败: {e}")

    # ========== 可视化完整室内场景 ===========
    print("\n=== 完整室内场景布局 ===")
    print("房间布局:")
    print("- 客厅: 左侧区域 (0-7m x 3-12m)")
    print("- 卧室: 右上区域 (7-15m x 3-12m)")
    print("- 厨房: 左下区域 (0-7m x 0-3m)")
    print("- 卫生间: 右下区域 (12-15m x 0-3m)")
    print("房间通道位置:")
    print("- 客厅↔卧室: (7.0, 5.5)")
    print("- 客厅↔厨房: (7.0, 1.5)")
    print("- 厨房↔卫生间: (12.0, 1.5)")
    print("- 卧室↔卫生间: (12.0, 5.5)")

    # 可视化墙体布局
    plot_map(map_rep, show_grid=False, show_legend=False, figsize=(15, 12))

# ========== A*路径规划测试 ===========
print("\n=== A*路径规划测试 ===")

# 获取分辨率（从地图或使用默认值）
resolution = config.get_grid_resolution()

# 使用配置文件中指定的碰撞边缘
collision_margin = config.get_collision_margin()
print(f"使用碰撞边缘: {collision_margin}m")

# 测试从客厅到卧室的路径
start = (3.0, 7.5)  # 客厅中央
goal = (10.0, 8.0)   # 卧室中央
astar_path = astar_search(map_rep.grid_map, start, goal, resolution, collision_margin=collision_margin)
if astar_path is not None:
    add_path(map_rep, astar_path, path_id="living_to_bedroom")
    print(f"A*路径 (客厅到卧室): {len(astar_path.points)} 个点")
else:
    print("A*未找到从客厅到卧室的可行路径！")

# 测试从厨房到卫生间的路径
start2 = (3.0, 1.5)  # 厨房
goal2 = (13.0, 1.0)  # 卫生间
astar_path2 = astar_search(map_rep.grid_map, start2, goal2, resolution, collision_margin=collision_margin)
if astar_path2 is not None:
    add_path(map_rep, astar_path2, path_id="kitchen_to_bathroom")
    print(f"A*路径 (厨房到卫生间): {len(astar_path2.points)} 个点")
else:
    print("A*未找到从厨房到卫生间的可行路径！")

# 测试从客厅到厨房的路径
start3 = (3.0, 7.5)  # 客厅
goal3 = (3.5, 2.5)   # 厨房
astar_path3 = astar_search(map_rep.grid_map, start3, goal3, resolution, collision_margin=collision_margin)
if astar_path3 is not None:
    add_path(map_rep, astar_path3, path_id="living_to_kitchen")
    print(f"A*路径 (客厅到厨房): {len(astar_path3.points)} 个点")
else:
    print("A*未找到从客厅到厨房的可行路径！")

# 测试从卧室到卫生间的路径
start4 = (10.0, 8.0)  # 卧室
goal4 = (13.0, 1.0)   # 卫生间
astar_path4 = astar_search(map_rep.grid_map, start4, goal4, resolution, collision_margin=collision_margin)
if astar_path4 is not None:
    add_path(map_rep, astar_path4, path_id="bedroom_to_bathroom")
    print(f"A*路径 (卧室到卫生间): {len(astar_path4.points)} 个点")
else:
    print("A*未找到从卧室到卫生间的可行路径！")

# 可视化最终结果
print("\n=== 最终路径规划结果 ===")
    plot_map(map_rep, show_grid=True, show_legend=False, figsize=(15, 12))

# ========== 保存地图到文件 ===========
print("\n=== 保存地图 ===")
try:
    # 保存完整室内场景地图
    save_path = "data/maps/complete_indoor_scene.json"
    saved_file = map_rep.save_to_json(save_path)
    print(f"✅ 地图已成功保存到: {saved_file}")
    print(f"地图信息:")
    print(f"- 地图ID: {map_rep.map_id}")
    print(f"- 画布大小: {map_rep.canvas_size}")
    print(f"- 物体数量: {len(map_rep.objects)}")
    print(f"- 栅格地图大小: {map_rep.grid_map.shape if map_rep.grid_map is not None else 'None'}")
    print(f"- 分辨率: {resolution}m")
    
    # 显示房间布局信息
    print(f"\n房间布局:")
    print(f"- 客厅: 左侧区域 (0-7m x 3-12m)")
    print(f"- 卧室: 右上区域 (7-15m x 3-12m)")
    print(f"- 厨房: 左下区域 (0-7m x 0-3m)")
    print(f"- 卫生间: 右下区域 (12-15m x 0-3m)")
    
except Exception as e:
    print(f"❌ 保存地图失败: {e}")