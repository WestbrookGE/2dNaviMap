"""
Grid Map PNG存储工具
提供grid_map的PNG格式存储和加载功能
"""

import os
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Optional, Tuple
from utils.config import config


class GridMapStorage:
    """Grid Map PNG存储管理类"""
    
    @staticmethod
    def save_grid_map_as_png(grid_map: np.ndarray, map_id: str, 
                            canvas_size: Tuple[float, float], 
                            resolution: float) -> str:
        """
        将grid_map保存为PNG文件
        
        Args:
            grid_map: numpy数组，形状为(height, width)
            map_id: 地图ID
            canvas_size: 画布大小 (width, height)
            resolution: 网格分辨率
            
        Returns:
            PNG文件的绝对路径
        """
        # 确保存储目录存在
        png_dir = config.get_png_directory()
        png_path = Path(png_dir)
        png_path.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        filename = f"{map_id}_grid_map.png"
        file_path = png_path / filename
        
        # 将numpy数组转换为PIL图像
        # 0表示障碍物（黑色），1表示可通行区域（白色）
        # 转换为0-255的灰度值
        img_array = grid_map.astype(np.uint8) * 255
        img = Image.fromarray(img_array, mode='L')
        
        # 保存PNG文件
        img.save(file_path, 'PNG')
        
        return str(file_path.absolute())
    
    @staticmethod
    def load_grid_map_from_png(map_id: str, canvas_size: Tuple[float, float], 
                              resolution: float) -> Optional[np.ndarray]:
        """
        从PNG文件加载grid_map
        
        Args:
            map_id: 地图ID
            canvas_size: 画布大小 (width, height)
            resolution: 网格分辨率
            
        Returns:
            numpy数组，如果文件不存在则返回None
        """
        # 构建文件路径
        png_dir = config.get_png_directory()
        filename = f"{map_id}_grid_map.png"
        file_path = Path(png_dir) / filename
        
        if not file_path.exists():
            return None
        
        # 加载PNG图像
        img = Image.open(file_path)
        img_array = np.array(img, dtype=np.uint8)
        
        # 转换为0-1的二进制值
        # 0表示障碍物，1表示可通行区域
        grid_map = (img_array > 127).astype(np.uint8)
        
        return grid_map
    
    @staticmethod
    def get_grid_map_path(map_id: str) -> str:
        """
        获取grid_map PNG文件的路径
        
        Args:
            map_id: 地图ID
            
        Returns:
            PNG文件的绝对路径
        """
        png_dir = config.get_png_directory()
        filename = f"{map_id}_grid_map.png"
        file_path = Path(png_dir) / filename
        return str(file_path.absolute())
    
    @staticmethod
    def grid_map_exists(map_id: str) -> bool:
        """
        检查grid_map PNG文件是否存在
        
        Args:
            map_id: 地图ID
            
        Returns:
            文件是否存在
        """
        file_path = GridMapStorage.get_grid_map_path(map_id)
        return os.path.exists(file_path)
    
    @staticmethod
    def delete_grid_map(map_id: str) -> bool:
        """
        删除grid_map PNG文件
        
        Args:
            map_id: 地图ID
            
        Returns:
            是否成功删除
        """
        file_path = GridMapStorage.get_grid_map_path(map_id)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False 