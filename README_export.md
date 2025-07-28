# 物体信息导出功能

## 功能概述

这个功能允许您导出 `data/objects` 目录中所有物体的信息，支持多种格式和输出方式。

## 功能特性

- ✅ 支持导出所有物体信息到 JSON 格式
- ✅ 支持导出所有物体信息到 CSV 格式  
- ✅ 提供物体信息摘要统计
- ✅ 命令行界面支持
- ✅ 错误处理和异常捕获
- ✅ 支持自定义输出文件路径

## 使用方法

### 1. 命令行使用

#### 显示物体信息摘要
```bash
python export.py --summary
```

#### 导出到 JSON 格式
```bash
python export.py --export --format json
```

#### 导出到 CSV 格式
```bash
python export.py --export --format csv
```

#### 指定输出文件路径
```bash
python export.py --export --format json --output my_objects.json
python export.py --export --format csv --output my_objects.csv
```

### 2. 编程接口使用

#### 基本用法
```python
from utils.object_exporter import ObjectExporter

# 创建导出器实例
exporter = ObjectExporter()

# 显示摘要
exporter.print_summary()

# 导出到 JSON
json_file = exporter.export_to_json("objects.json")

# 导出到 CSV
csv_file = exporter.export_to_csv("objects.csv")
```

#### 便捷函数
```python
from utils.object_exporter import export_objects_info

# 导出到 JSON
result_file = export_objects_info("json", "output.json")

# 导出到 CSV
result_file = export_objects_info("csv", "output.csv")
```

## 输出格式说明

### JSON 格式
```json
{
  "chair": {
    "label": "chair",
    "size": [0.6, 0.6, 0.9],
    "position": [0.0, 0.0, 0.0]
  },
  "sofa": {
    "label": "sofa", 
    "size": [2.0, 0.9, 0.8],
    "position": [0.0, 0.0, 0.0]
  }
}
```

### CSV 格式
```csv
object_name,label,size_x,size_y,size_z,position_x,position_y,position_z
chair,chair,0.6,0.6,0.9,0.0,0.0,0.0
sofa,sofa,2.0,0.9,0.8,0.0,0.0,0.0
```

## 物体信息结构

每个物体包含以下信息：

- **label**: 物体标签/名称
- **size**: 物体尺寸 [x, y, z]
- **position**: 物体位置 [x, y, z]

## 统计信息

导出功能还提供以下统计信息：

- 总物体数量
- 唯一标签列表
- 各标签的物体数量
- 平均尺寸统计
- 完整的物体列表

## 测试

运行测试脚本来验证功能：

```bash
python test_export.py
```

## 错误处理

- 自动处理文件读取错误
- 自动创建输出目录
- 提供详细的错误信息
- 支持中文路径和文件名

## 依赖

- Python 3.6+
- 标准库：json, csv, pathlib, typing
- 无需额外第三方依赖 