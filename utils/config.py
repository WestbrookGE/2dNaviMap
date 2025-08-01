import yaml
import os
from typing import Dict, Any, List, Tuple

class Config:
    """配置管理类，负责读取和管理所有配置参数"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"警告: 配置文件 {config_path} 未找到，使用默认配置")
            self._config = self._get_default_config()
        except Exception as e:
            print(f"警告: 读取配置文件失败: {e}，使用默认配置")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'grid_map': {
                'resolution': 0.01,
                'default_resolution': 0.01,
                'png_storage': True,
                'png_directory': 'data/grid_maps'
            },
            'collision': {
                'margin': 0.3,
                'margins': [0.0, 0.2, 0.3]
            },
            'pathfinding': {
                'max_search_radius': 2.0,
                'sample_step': 0.05
            },
            'map': {
                'default_canvas_size': [15.0, 12.0]
            },
            'visualization': {
                'alpha': 0.3
            },
            'objects': {
                'default_size': [0.3, 0.3, 0.6]
            }
        }
    
    def reload_config(self):
        """重新加载配置文件"""
        self._load_config()
    
    def get(self, key: str, default=None) -> Any:
        """获取配置值，支持点号分隔的嵌套键"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_grid_resolution(self) -> float:
        """获取网格分辨率"""
        return self.get('grid_map.resolution', 0.01)
    
    def get_default_resolution(self) -> float:
        """获取默认分辨率"""
        return self.get('grid_map.default_resolution', 0.01)
    
    def get_png_storage_enabled(self) -> bool:
        """获取是否启用PNG存储"""
        return self.get('grid_map.png_storage', True)
    
    def get_png_directory(self) -> str:
        """获取PNG存储目录"""
        return self.get('grid_map.png_directory', 'data/grid_maps')
    
    def get_collision_margin(self) -> float:
        """获取碰撞边缘距离"""
        return self.get('collision.margin', 0.3)
    
    def get_collision_margins(self) -> List[float]:
        """获取碰撞边缘选项列表"""
        return self.get('collision.margins', [0.0, 0.2, 0.3])
    
    def get_max_search_radius(self) -> float:
        """获取最大搜索半径"""
        return self.get('pathfinding.max_search_radius', 2.0)
    
    def get_sample_step(self) -> float:
        """获取路径采样步长"""
        return self.get('pathfinding.sample_step', 0.05)
    
    def get_default_canvas_size(self) -> Tuple[float, float]:
        """获取默认画布大小"""
        size = self.get('map.default_canvas_size', [15.0, 12.0])
        return tuple(size)
    
    def get_visualization_alpha(self) -> float:
        """获取可视化透明度"""
        return self.get('visualization.alpha', 0.3)
    
    def get_default_object_size(self) -> List[float]:
        """获取默认对象尺寸"""
        return self.get('objects.default_size', [0.3, 0.3, 0.6])

# 创建全局配置实例
config = Config()
