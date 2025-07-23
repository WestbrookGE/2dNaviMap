from apis.interaction_api import create_map, add_object_from_file
from utils.visualization import plot_map
from core.data_structures import SourceType
import os

# 新建地图
canvas_size = (8.0, 6.0)  # 8米x6米
map_rep = create_map(map_id="demo_map", canvas_size=canvas_size, source_type=SourceType.OTHER)

# 合理布局五个物体（位置为左下底角）
object_positions = {
    "bed": (1.5, 1.0, 0.0),        # 靠左下
    "table": (4.0, 1.5, 0.0),     # 靠下中间
    "fridge": (7.0, 1.0, 0.0),      # 靠右下
    "wardrobe": (4.0, 5.0, 0.0),    # 靠右上
    "sofa": (1.5, 4.5, 0.0),        # 靠左上
}

for obj_name, pos in object_positions.items():
    add_object_from_file(map_rep, obj_name, object_dir=os.path.join("data", "objects"), new_position=pos)

# 可视化
plot_map(map_rep, show_grid=False, figsize=(10, 8)) 

# print(map_rep.objects["bed_1"].to_dict())