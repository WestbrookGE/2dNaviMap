# 碰撞边缘可视化功能

## 功能概述

在可视化地图时，为所有物体添加碰撞边缘显示，与A*算法中的碰撞体积扩展保持一致。

## 主要特性

### 1. 碰撞边缘计算
- 使用 `expand_bbox_for_collision()` 函数计算扩展后的边界框
- 碰撞边缘距离可通过配置文件 `config.yaml` 中的 `collision.margin` 参数设置
- 默认碰撞边缘距离为 0.3 米

### 2. 可视化效果
- **实心矩形**：物体的实际边界（原有显示）
- **红色虚线**：碰撞边缘（新增功能）
- **蓝色虚线**：机器人的碰撞边缘（如果存在机器人状态）

### 3. 物体类型区分
- **墙体**：深灰色实心，黑色边框
- **门**：棕色实心，深红色虚线边框
- **家具**：浅蓝色实心，蓝色边框
- **机器人**：蓝色实心，蓝色虚线碰撞边缘

## 使用方法

### 基本用法
```python
from utils.visualization import plot_map
from core.data_structures import MapRepresentation

# 显示碰撞边缘（默认）
plot_map(map_rep, show_collision_margin=True)

# 不显示碰撞边缘
plot_map(map_rep, show_collision_margin=False)
```

### 从JSON文件加载
```python
from utils.visualization import plot_from_json

# 显示碰撞边缘
plot_from_json("path/to/map.json", show_collision_margin=True)
```

## 配置参数

在 `config.yaml` 文件中可以调整以下参数：

```yaml
collision:
  margin: 0.3  # 碰撞边缘距离（米）
  margins: [0.0, 0.2, 0.3]  # 可选的碰撞边缘选项
```

## 与A*算法的关联

碰撞边缘可视化与 `planners/astar.py` 中的碰撞体积扩展功能保持一致：

1. **相同的扩展逻辑**：都使用 `expand_obstacles()` 函数
2. **相同的配置参数**：都使用 `config.get_collision_margin()`
3. **相同的扩展距离**：确保可视化与实际路径规划使用相同的碰撞体积

## 测试

运行测试脚本查看效果：
```bash
python test_simple_collision.py
```

## 技术实现

### 核心函数

```python
def expand_bbox_for_collision(bbox_2d: Tuple[float, float, float, float], 
                             collision_margin: float = None) -> Tuple[float, float, float, float]:
    """
    为物体的2D边界框添加碰撞边缘
    """
    if collision_margin is None:
        collision_margin = config.get_collision_margin()
    
    if collision_margin <= 0:
        return bbox_2d
    
    min_x, min_y, max_x, max_y = bbox_2d
    return (min_x - collision_margin, min_y - collision_margin, 
            max_x + collision_margin, max_y + collision_margin)
```

### 可视化增强

在 `plot_map()` 函数中：
1. 为每个物体绘制原始边界框
2. 计算并绘制碰撞边缘（红色虚线）
3. 为机器人绘制碰撞边缘（蓝色虚线）
4. 在标题中显示碰撞边缘距离

## 优势

1. **直观性**：用户可以直观地看到A*算法考虑的碰撞体积
2. **一致性**：可视化与实际路径规划使用相同的参数
3. **可配置性**：可以通过配置文件调整碰撞边缘距离
4. **灵活性**：可以选择显示或隐藏碰撞边缘 