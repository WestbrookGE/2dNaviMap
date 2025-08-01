from typing import List, Tuple, Dict, Optional, Any
from enum import Enum
import numpy as np
import json
import os
from utils.config import config
from utils.grid_map_storage import GridMapStorage

class SourceType(Enum):
    GAUSSIAN_SPLATTING = "GAUSSIAN_SPLATTING"
    ISAAC_SIM = "ISAAC_SIM"
    OTHER = "OTHER"

class MapObject:
    def __init__(
        self,
        label: str,
        size: Tuple[float, float, float],  # 长宽高，必要属性
        position: Tuple[float, float, float] = (0.0, 0.0, 0.0),  # 左下底角位置，必要属性
        id: Optional[str] = None,
    ):
        self.label = label
        self.size = size
        self.position = position
        # 如果没有提供id，使用label_0格式
        self.id = id or f"{label}_0"

    def get_bbox_3d(self) -> Tuple[float, float, float, float, float, float]:
        """获取3D边界框 (min_x, min_y, min_z, max_x, max_y, max_z)"""
        x, y, z = self.position
        w, d, h = self.size
        return (x, y, z, x + w, y + d, z + h)

    def get_centroid_3d(self) -> Tuple[float, float, float]:
        """获取3D质心坐标"""
        x, y, z = self.position
        w, d, h = self.size
        return (x + w/2, y + d/2, z + h/2)

    def get_bbox_2d(self) -> Tuple[float, float, float, float]:
        """获取2D边界框 (min_x, min_y, max_x, max_y)"""
        x, y, z = self.position
        w, d, h = self.size
        return (x, y, x + w, y + d)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "size": self.size,
            "position": self.position,
            "id": self.id,
        }

    @staticmethod
    def from_dict(data: dict) -> "MapObject":
        return MapObject(
            label=data["label"],
            size=tuple(data["size"]),
            position=tuple(data.get("position", (0.0, 0.0, 0.0))),
            id=data.get("id"),
        )

    @staticmethod
    def load_from_json(path: str) -> "MapObject":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return MapObject.from_dict(data)

class AgentState:
    def __init__(
        self,
        agent_id: str,
        size: Tuple[float, float],  # 机器人长宽
        position: Tuple[float, float],
        orientation: float,
    ):
        self.agent_id = agent_id
        self.size = size
        self.position = position
        self.orientation = orientation

    def get_bbox_2d(self) -> Tuple[float, float, float, float]:
        """获取2D边界框 (min_x, min_y, max_x, max_y)"""
        x, y = self.position
        w, d = self.size
        return (x, y, x + w, y + d)

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "size": self.size,
            "position": self.position,
            "orientation": self.orientation,
        }

    @staticmethod
    def from_dict(data: dict) -> "AgentState":
        return AgentState(
            agent_id=data["agent_id"],
            size=tuple(data["size"]),
            position=tuple(data["position"]),
            orientation=data["orientation"],
        )

    @staticmethod
    def load_from_json(path: str) -> "AgentState":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AgentState.from_dict(data)

class MapRepresentation:
    def __init__(
        self,
        map_id: str,
        source_type: SourceType,
        objects: Dict[str, MapObject],
        grid_map: Optional[np.ndarray] = None,
        scene_description: Optional[str] = None,
        canvas_size: Optional[Tuple[float, float]] = None,  # 新增画布大小属性
    ):
        self.map_id = map_id
        self.source_type = source_type
        self.objects = objects
        self.grid_map = grid_map
        self.scene_description = scene_description or ""
        self.canvas_size = canvas_size  # 新增

    def to_dict(self) -> dict:
        """转换为字典，不包含grid_map数据"""
        return {
            "map_id": self.map_id,
            "source_type": self.source_type.value,
            "objects": {k: v.to_dict() for k, v in self.objects.items()},
            "scene_description": self.scene_description,
            "canvas_size": self.canvas_size,  # 新增
        }

    @staticmethod
    def from_dict(data: dict) -> "MapRepresentation":
        objects = {k: MapObject.from_dict(v) for k, v in data["objects"].items()}
        return MapRepresentation(
            map_id=data["map_id"],
            source_type=SourceType(data["source_type"]),
            objects=objects,
            grid_map=None,  # grid_map现在通过PNG文件管理
            scene_description=data.get("scene_description", ""),
            canvas_size=tuple(data["canvas_size"]) if data.get("canvas_size") is not None else None,  # 新增
        )

    @staticmethod
    def load_from_json(path: str) -> "MapRepresentation":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        map_rep = MapRepresentation.from_dict(data)
        
        # 尝试从PNG文件加载grid_map
        if map_rep.canvas_size is not None:
            resolution = config.get_default_resolution()
            grid_map = GridMapStorage.load_grid_map_from_png(
                map_rep.map_id, map_rep.canvas_size, resolution
            )
            map_rep.grid_map = grid_map
        
        return map_rep
    
    def save_to_json(self, path: str) -> str:
        """
        保存地图到JSON文件
        
        Args:
            path: 保存路径
            
        Returns:
            保存文件的绝对路径
        """
        import os
        from pathlib import Path
        
        # 确保目录存在
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存到文件
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            
        return str(save_path.absolute())
    
    def save_grid_map_as_png(self) -> Optional[str]:
        """
        将grid_map保存为PNG文件
        
        Returns:
            PNG文件路径，如果保存失败则返回None
        """
        if self.grid_map is None or self.canvas_size is None:
            return None
        
        try:
            resolution = config.get_default_resolution()
            return GridMapStorage.save_grid_map_as_png(
                self.grid_map, self.map_id, self.canvas_size, resolution
            )
        except Exception as e:
            print(f"保存grid_map PNG文件失败: {e}")
            return None
    
    def load_grid_map_from_png(self) -> bool:
        """
        从PNG文件加载grid_map
        
        Returns:
            是否成功加载
        """
        if self.canvas_size is None:
            return False
        
        try:
            resolution = config.get_default_resolution()
            grid_map = GridMapStorage.load_grid_map_from_png(
                self.map_id, self.canvas_size, resolution
            )
            if grid_map is not None:
                self.grid_map = grid_map
                return True
            return False
        except Exception as e:
            print(f"加载grid_map PNG文件失败: {e}")
            return False
    
    def get_grid_map_path(self) -> str:
        """
        获取grid_map PNG文件路径
        
        Returns:
            PNG文件路径
        """
        return GridMapStorage.get_grid_map_path(self.map_id)
    
    def grid_map_exists(self) -> bool:
        """
        检查grid_map PNG文件是否存在
        
        Returns:
            文件是否存在
        """
        return GridMapStorage.grid_map_exists(self.map_id)
    
    def delete_grid_map(self) -> bool:
        """
        删除grid_map PNG文件
        
        Returns:
            是否成功删除
        """
        return GridMapStorage.delete_grid_map(self.map_id)

class Path:
    def __init__(self, points: List[Tuple[float, float]]):
        self.points = points

    def to_dict(self) -> dict:
        return {"points": self.points}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @staticmethod
    def from_dict(data: dict) -> "Path":
        return Path(points=[tuple(pt) for pt in data["points"]])

    @staticmethod
    def load_from_json(path: str) -> "Path":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Path.from_dict(data)
