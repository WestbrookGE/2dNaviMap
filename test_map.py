from apis.interaction_api import create_map, add_object_from_file, update_grid_map_full, add_object_with_collision_check, add_wall, add_path
from utils.visualization import plot_map
from core.data_structures import SourceType, Path
import os
from planners.astar import astar_search

# 新建地图
canvas_size = (8.0, 6.0)  # 8米x6米
resolution = 0.1  # 精度0.1米
map_rep = create_map(map_id="demo_map", canvas_size=canvas_size, source_type=SourceType.OTHER)
update_grid_map_full(map_rep, resolution=resolution)
# 合理布局五个物体（位置为左下底角）
object_positions = {
    "bed": (1.5, 1.0, 0.0),        # 靠左下
    "table": (4.0, 1.5, 0.0),     # 靠下中间
    "fridge": (7.0, 1.0, 0.0),      # 靠右下
    "wardrobe": (4.0, 5.0, 0.0),    # 靠右上
    "sofa": (1.5, 4.5, 0.0),        # 靠左上
}

for obj_name, pos in object_positions.items():
    # add_object_from_file(map_rep, obj_name, object_dir=os.path.join("data", "objects"), new_position=pos)
    add_object_with_collision_check(map_rep, obj_name, object_dir=os.path.join("data", "objects"), new_position=pos, resolution=resolution)

# 添加一段墙体（例如横跨下方的墙）
wall_id = "wall_bottom"
wall_size = (8.0, 0.2, 2.5)  # 8米长，0.2米厚，2.5米高
wall_pos = (0.0, 0.0, 0.0)  # 沿底边
add_wall(map_rep, wall_id, wall_size, wall_pos, resolution=resolution)

# 可视化添加墙体后的地图
plot_map(map_rep, show_grid=False, figsize=(10, 8))


# ========== A*算法测试 ===========
start = (0.5, 0.3)  # y=0.3，避开底部墙体
goal = (4.5, 5.8)
astar_path = astar_search(map_rep.grid_map, start, goal, resolution)
if astar_path is not None:
    add_path(map_rep, astar_path, path_id="astar_path")
    print("A*路径:", astar_path.points)
    plot_map(map_rep, show_grid=True, figsize=(10, 8))
else:
    print("A*未找到可行路径！")
# print(map_rep.objects["bed_1"].to_dict())