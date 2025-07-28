import json
import os
from typing import Dict, List, Any
from pathlib import Path


class ObjectExporter:
    """物体信息导出器"""
    
    def __init__(self, objects_dir: str = "data/objects"):
        """
        初始化物体导出器
        
        Args:
            objects_dir: 物体文件目录路径
        """
        self.objects_dir = Path(objects_dir)
        
    def load_all_objects(self) -> Dict[str, Dict[str, Any]]:
        """
        加载所有物体信息
        
        Returns:
            包含所有物体信息的字典，键为文件名（不含扩展名），值为物体数据
        """
        objects_data = {}
        
        if not self.objects_dir.exists():
            raise FileNotFoundError(f"物体目录不存在: {self.objects_dir}")
            
        for json_file in self.objects_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    object_data = json.load(f)
                    # 使用文件名（不含扩展名）作为键
                    object_name = json_file.stem
                    objects_data[object_name] = object_data
            except Exception as e:
                print(f"加载文件 {json_file} 时出错: {e}")
                
        return objects_data
    
    def export_to_json(self, output_file: str = "exported_objects.json") -> str:
        """
        导出所有物体信息到JSON文件
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            输出文件的绝对路径
        """
        objects_data = self.load_all_objects()
        
        # 创建输出目录（如果不存在）
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(objects_data, f, ensure_ascii=False, indent=2)
            
        return str(output_path.absolute())
    
    def export_to_csv(self, output_file: str = "exported_objects.csv") -> str:
        """
        导出所有物体信息到CSV文件
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            输出文件的绝对路径
        """
        import csv
        
        objects_data = self.load_all_objects()
        
        # 创建输出目录（如果不存在）
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入CSV文件
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入表头
            writer.writerow(['object_name', 'label', 'size_x', 'size_y', 'size_z', 'position_x', 'position_y', 'position_z'])
            
            # 写入数据
            for object_name, object_data in objects_data.items():
                label = object_data.get('label', '')
                size = object_data.get('size', [0, 0, 0])
                position = object_data.get('position', [0, 0, 0])
                
                writer.writerow([
                    object_name,
                    label,
                    size[0] if len(size) > 0 else 0,
                    size[1] if len(size) > 1 else 0,
                    size[2] if len(size) > 2 else 0,
                    position[0] if len(position) > 0 else 0,
                    position[1] if len(position) > 1 else 0,
                    position[2] if len(position) > 2 else 0
                ])
                
        return str(output_path.absolute())
    
    def get_objects_summary(self) -> Dict[str, Any]:
        """
        获取物体信息摘要
        
        Returns:
            包含物体统计信息的字典
        """
        objects_data = self.load_all_objects()
        
        # 统计信息
        total_objects = len(objects_data)
        labels = [obj.get('label', '') for obj in objects_data.values()]
        unique_labels = list(set(labels))
        
        # 按标签分组统计
        label_counts = {}
        for label in labels:
            label_counts[label] = label_counts.get(label, 0) + 1
            
        # 尺寸统计
        sizes = [obj.get('size', [0, 0, 0]) for obj in objects_data.values()]
        avg_sizes = {
            'x': sum(s[0] for s in sizes) / len(sizes) if sizes else 0,
            'y': sum(s[1] for s in sizes) / len(sizes) if sizes else 0,
            'z': sum(s[2] for s in sizes) / len(sizes) if sizes else 0
        }
        
        return {
            'total_objects': total_objects,
            'unique_labels': unique_labels,
            'label_counts': label_counts,
            'average_sizes': avg_sizes,
            'objects_list': list(objects_data.keys())
        }
    
    def print_summary(self):
        """打印物体信息摘要到控制台"""
        summary = self.get_objects_summary()
        
        print("=== 物体信息摘要 ===")
        print(f"总物体数量: {summary['total_objects']}")
        print(f"唯一标签数量: {len(summary['unique_labels'])}")
        print("\n标签统计:")
        for label, count in summary['label_counts'].items():
            print(f"  {label}: {count}个")
        print(f"\n平均尺寸: {summary['average_sizes']}")
        print(f"\n物体列表: {', '.join(summary['objects_list'])}")


def export_objects_info(output_format: str = "json", output_file: str = None) -> str:
    """
    导出所有物体信息的便捷函数
    
    Args:
        output_format: 输出格式 ("json" 或 "csv")
        output_file: 输出文件路径（可选）
        
    Returns:
        输出文件的绝对路径
    """
    exporter = ObjectExporter()
    
    if output_file is None:
        if output_format.lower() == "json":
            output_file = "exported_objects.json"
        elif output_format.lower() == "csv":
            output_file = "exported_objects.csv"
        else:
            raise ValueError("不支持的输出格式，请使用 'json' 或 'csv'")
    
    if output_format.lower() == "json":
        return exporter.export_to_json(output_file)
    elif output_format.lower() == "csv":
        return exporter.export_to_csv(output_file)
    else:
        raise ValueError("不支持的输出格式，请使用 'json' 或 'csv'")


if __name__ == "__main__":
    # 示例用法
    exporter = ObjectExporter()
    
    # 打印摘要
    exporter.print_summary()
    
    # 导出到JSON
    json_file = exporter.export_to_json()
    print(f"\n已导出到JSON文件: {json_file}")
    
    # 导出到CSV
    csv_file = exporter.export_to_csv()
    print(f"已导出到CSV文件: {csv_file}") 