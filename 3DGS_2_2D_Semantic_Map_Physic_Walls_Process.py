import os
import numpy as np
import json
from PIL import Image
from shapely.geometry import Polygon, Point
from scipy.ndimage import label as nd_label  # 用于墙体分块

def format2(x):
    return "{:.2f}".format(float(x))

root_dir = "./Dataset/InteriorGS"
output_root = "./results_Walls"
os.makedirs(output_root, exist_ok=True)

for subdir in sorted(os.listdir(root_dir)):
    dir_path = os.path.join(root_dir, subdir)
    if not os.path.isdir(dir_path):
        continue
    try:
        id_str = subdir.split("_")[-1]
    except:
        continue
    out_json = os.path.join(output_root, f"2D_Semantic_Map_{id_str}.json")
    if os.path.exists(out_json):
        print(f"已存在 {out_json}，跳过")
        continue
    occ_json_path = os.path.join(dir_path, "occupancy.json")
    label_json_path = os.path.join(dir_path, "labels.json")
    occ_img_path = os.path.join(dir_path, "occupancy.png")
    if not (os.path.isfile(occ_json_path) and os.path.isfile(label_json_path) and os.path.isfile(occ_img_path)):
        print(f"跳过 {subdir}, 缺少必需的json/png文件")
        continue
    # ===== 读取Occupancy map参数 =====
    with open(occ_json_path, "r") as f:
        meta = json.load(f)
    scale = meta["scale"]
    x_min, y_min = meta["min"][:2]
    x_max, y_max = meta["max"][:2]
    occ_img = Image.open(occ_img_path).convert("L")
    occupancy = np.array(occ_img)
    h, w = occupancy.shape
    # ===== 读取资产标注 =====
    with open(label_json_path, "r") as f:
        labels = json.load(f)
    label2id = {}
    id2label = {}
    label_cur = 1
    for obj in labels:
        label = obj["label"]
        if label not in label2id:
            label2id[label] = label_cur
            id2label[label_cur] = label
            label_cur += 1
    result_list = []
    # ====== 资产实例处理 ======
    for obj in labels:
        if "bounding_box" not in obj: continue
        label = obj["label"]
        cat_id = label2id[label]
        poly3d = obj["bounding_box"]
        poly2d = [[v["x"], v["y"]] for v in poly3d[:4]]
        poly = Polygon(poly2d)
        xys = np.array(poly2d)
        min_x_pixel = int(np.floor((np.min(xys[:, 0]) - x_min) / scale))
        max_x_pixel = int(np.floor((np.max(xys[:, 0]) - x_min) / scale))
        min_y_pixel = int(np.floor((np.min(xys[:, 1]) - y_min) / scale))
        max_y_pixel = int(np.floor((np.max(xys[:, 1]) - y_min) / scale))
        min_x_pixel = np.clip(min_x_pixel, 0, w - 1)
        max_x_pixel = np.clip(max_x_pixel, 0, w - 1)
        min_y_pixel = np.clip(min_y_pixel, 0, h - 1)
        max_y_pixel = np.clip(max_y_pixel, 0, h - 1)
        mask = np.zeros((h, w), dtype=bool)
        for j in range(min_x_pixel, max_x_pixel + 1):
            for i in range(min_y_pixel, max_y_pixel + 1):
                i_flip = h - 1 - i
                j_flip = w - 1 - j
                cx = x_min + (j + 0.5) * scale
                cy = y_min + (i + 0.5) * scale
                p = Point(cx, cy)
                if poly.covers(p):
                    mask[i_flip, j_flip] = True
        ys, xs = np.where(mask)
        if xs.size == 0 or ys.size == 0:
            continue
        xmin_pix, xmax_pix = min(xs), max(xs)
        ymin_pix, ymax_pix = min(ys), max(ys)
        x_left = x_min + xmin_pix * scale
        x_right = x_min + (xmax_pix + 1) * scale
        y_bottom = y_min + ymin_pix * scale
        y_top = y_min + (ymax_pix + 1) * scale
        w_box = x_right - x_left
        h_box = y_top - y_bottom
        bbox_m = [
            format2(x_left),
            format2(y_bottom),
            format2(x_right),
            format2(y_top)
        ]
        bbox_xywh_m = [
            format2(x_left),
            format2(y_bottom),
            format2(w_box),
            format2(h_box)
        ]
        mask_coords_m = [
            [format2(y_min + (y + 0.5) * scale), format2(x_min + (x + 0.5) * scale)]
            for y, x in zip(ys, xs)
        ]
        result_list.append({
            "category_id": int(cat_id),
            "category_label": label,
            "instance_id": obj.get("ins_id", ""),
            "bbox_m": bbox_m,
            "bbox_xywh_m": bbox_xywh_m,
            "area": int(mask.sum()),
            "mask_coords_m": mask_coords_m
        })

    # ======= occupancy墙体（上下flip+左移shift，连通域分块wall）=======
    shift = 1
    pixels, counts = np.unique(occupancy.reshape(-1), return_counts=True)
    candidate_walls = [int(p) for p in pixels if 0 < p < 250]
    if candidate_walls:
        wall_value = int(candidate_walls[np.argmax([counts[np.where(pixels==v)[0][0]] for v in candidate_walls])])
    else:
        wall_value = int(pixels[0])
    wall_cat_id = max(label2id.values(), default=0) + 1
    wall_mask = (occupancy == wall_value)
    wall_mask_flip = np.flipud(wall_mask)
    if shift > 0:
        wall_mask_flip[:, :-shift] = wall_mask_flip[:, shift:]
        wall_mask_flip[:, -shift:] = 0

    structure = np.ones((3,3), dtype=np.int32)  # 8连通域
    wall_label_mask, wall_count = nd_label(wall_mask_flip, structure=structure)
    for idx in range(1, wall_count+1):
        block_mask = (wall_label_mask == idx)
        ys, xs = np.where(block_mask)
        if xs.size == 0 or ys.size == 0: continue
        xmin_pix, xmax_pix = xs.min(), xs.max()
        ymin_pix, ymax_pix = ys.min(), ys.max()
        x_left = x_min + xmin_pix * scale
        x_right = x_min + (xmax_pix + 1) * scale
        y_bottom = y_min + ymin_pix * scale
        y_top = y_min + (ymax_pix + 1) * scale
        w_box = x_right - x_left
        h_box = y_top - y_bottom
        bbox_m = [
            format2(x_left), format2(y_bottom), format2(x_right), format2(y_top)
        ]
        bbox_xywh_m = [
            format2(x_left), format2(y_bottom), format2(w_box), format2(h_box)
        ]
        mask_coords_m = [
            [format2(y_min + (y + 0.5) * scale), format2(x_min + (x + 0.5) * scale)]
            for y, x in zip(ys, xs)
        ]
        result_list.append({
            "category_id": int(wall_cat_id),
            "category_label": "wall",
            "instance_id": f"wall_{idx}",
            "bbox_m": bbox_m,
            "bbox_xywh_m": bbox_xywh_m,
            "area": int(block_mask.sum()),
            "mask_coords_m": mask_coords_m,
        })
    with open(out_json, "w") as f:
        json.dump(result_list, f, indent=2)
    print(f"已处理: {out_json}")