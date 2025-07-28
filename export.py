#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2D地图中间件主程序
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from utils.object_exporter import ObjectExporter, export_objects_info


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="2D地图中间件 - 物体信息导出工具")
    parser.add_argument("--export", action="store_true", help="导出所有物体信息")
    parser.add_argument("--format", choices=["json", "csv"], default="json", 
                       help="导出格式 (默认: json)")
    parser.add_argument("--output", type=str, help="输出文件路径")
    parser.add_argument("--summary", action="store_true", help="显示物体信息摘要")
    
    args = parser.parse_args()
    
    if not any([args.export, args.summary]):
        parser.print_help()
        return
    
    try:
        exporter = ObjectExporter()
        
        if args.summary:
            exporter.print_summary()
        
        if args.export:
            output_file = args.output
            if output_file is None:
                if args.format == "json":
                    output_file = "exported_objects.json"
                else:
                    output_file = "exported_objects.csv"
            
            if args.format == "json":
                result_file = exporter.export_to_json(output_file)
            else:
                result_file = exporter.export_to_csv(output_file)
            
            print(f"\n✅ 物体信息已成功导出到: {result_file}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
