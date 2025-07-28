# 配置系统使用说明

## 概述

本项目现在使用统一的配置系统来管理所有配置参数。所有配置值都保存在 `config.yaml` 文件中，通过 `utils/config.py` 中的 `Config` 类来读取和管理。

## 配置文件结构

### config.yaml

```yaml
# 2D导航地图配置文件

# 网格地图配置
grid_map:
  resolution: 0.1  # 网格分辨率（米/格子）
  default_resolution: 1.0  # 默认分辨率

# 碰撞检测配置
collision:
  margin: 0.3  # 碰撞边缘距离（米）
  margins: [0.0, 0.2, 0.3]  # 多种碰撞边缘选项

# 路径规划配置
pathfinding:
  max_search_radius: 2.0  # 最大搜索半径（米）
  sample_step: 0.05  # 路径采样步长（米）

# 地图配置
map:
  default_canvas_size: [15.0, 12.0]  # 默认画布大小（米）

# 可视化配置
visualization:
  alpha: 0.3  # 透明度

# 对象配置
objects:
  default_size: [0.3, 0.3, 0.6]  # 默认对象尺寸
```

## 使用方法

### 1. 导入配置

```python
from utils.config import config
```

### 2. 读取配置值

#### 使用专用方法（推荐）

```python
# 网格地图配置
resolution = config.get_grid_resolution()  # 0.1
default_resolution = config.get_default_resolution()  # 1.0

# 碰撞检测配置
collision_margin = config.get_collision_margin()  # 0.3
collision_margins = config.get_collision_margins()  # [0.0, 0.2, 0.3]

# 路径规划配置
max_search_radius = config.get_max_search_radius()  # 2.0
sample_step = config.get_sample_step()  # 0.05

# 地图配置
canvas_size = config.get_default_canvas_size()  # (15.0, 12.0)

# 可视化配置
alpha = config.get_visualization_alpha()  # 0.3

# 对象配置
default_size = config.get_default_object_size()  # [0.3, 0.3, 0.6]
```

#### 使用通用方法

```python
# 使用点号分隔的键路径
resolution = config.get('grid_map.resolution')  # 0.1
collision_margin = config.get('collision.margin')  # 0.3

# 提供默认值
value = config.get('nonexistent.key', '默认值')
```

### 3. 在函数中使用配置

现在所有相关函数都支持使用配置值作为默认参数：

```python
# 在 planners/astar.py 中
def astar_search(grid_map, start, goal, resolution=None, collision_margin=None):
    if resolution is None:
        resolution = config.get_default_resolution()
    if collision_margin is None:
        collision_margin = config.get_collision_margin()
    # ... 函数实现

# 在 apis/interaction_api.py 中
def update_grid_map_full(map_rep, resolution=None):
    if resolution is None:
        resolution = config.get_default_resolution()
    # ... 函数实现
```

## 配置参数说明

### 网格地图配置 (grid_map)
- `resolution`: 网格分辨率，决定地图的精度
- `default_resolution`: 默认分辨率，用于未指定分辨率的情况

### 碰撞检测配置 (collision)
- `margin`: 碰撞边缘距离，用于扩展障碍物
- `margins`: 多种碰撞边缘选项，用于测试不同设置

### 路径规划配置 (pathfinding)
- `max_search_radius`: 最大搜索半径，用于寻找最近可行位置
- `sample_step`: 路径采样步长，用于碰撞检测

### 地图配置 (map)
- `default_canvas_size`: 默认画布大小

### 可视化配置 (visualization)
- `alpha`: 可视化透明度

### 对象配置 (objects)
- `default_size`: 默认对象尺寸

## 修改配置

### 方法1：直接编辑 config.yaml

```yaml
# 修改网格分辨率
grid_map:
  resolution: 0.05  # 改为更精细的分辨率

# 修改碰撞边缘
collision:
  margin: 0.5  # 增加碰撞边缘
```

### 方法2：程序运行时重新加载

```python
from utils.config import config

# 重新加载配置
config.reload_config()

# 获取更新后的配置
new_resolution = config.get_grid_resolution()
```

## 测试配置系统

运行测试脚本验证配置系统：

```bash
python test_config.py
```

## 依赖要求

确保安装了必要的依赖：

```bash
pip install -r requirements.txt
```

主要依赖：
- `PyYAML>=6.0`: 用于读取YAML配置文件
- `numpy>=1.21.0`: 数值计算
- `matplotlib>=3.5.0`: 可视化

## 优势

1. **集中管理**: 所有配置参数都在一个文件中
2. **易于修改**: 无需修改代码即可调整参数
3. **类型安全**: 提供专门的类型化访问方法
4. **向后兼容**: 函数参数保持可选，默认使用配置值
5. **容错性**: 配置文件不存在时使用默认值
6. **灵活性**: 支持运行时重新加载配置

## 注意事项

1. 修改配置文件后，程序会自动读取新配置
2. 如果配置文件不存在或读取失败，会使用内置的默认配置
3. 所有配置值都有合理的默认值，确保程序正常运行
4. 建议在修改配置前备份原始配置文件 