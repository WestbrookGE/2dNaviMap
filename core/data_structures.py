from typing import List, Tuple, Dict, Optional, Any
from enum import Enum
import numpy as np
import json
import os

class SourceType(Enum):
    GAUSSIAN_SPLATTING = "GAUSSIAN_SPLATTING"
    ISAAC_SIM = "ISAAC_SIM"
    OTHER = "OTHER"

class MapObject:
    def __init__(
        self,
        object_id: str,
        category: str,
        size: Tuple[float, float, float],  # 长宽高，必要属性
        position: Tuple[float, float, float] = (0.0, 0.0, 0.0),  # 左下底角位置，必要属性
        attributes: Optional[List[str]] = None,
        vertical_relation: Optional[Dict[str, Any]] = None,
    ):
        self.object_id = object_id
        self.category = category
        self.size = size
        self.position = position
        x, y, z = position
        w, d, h = size
        self.source_bbox_3d = (
            x, y, z,  # min_x, min_y, min_z
            x + w, y + d, z + h   # max_x, max_y, max_z
        )
        self.source_centroid_3d = (x + w/2, y + d/2, z + h/2)
        self.bbox_2d = (x, y, x + w, y + d)  # 新增2D bbox
        self.attributes = attributes or []
        self.vertical_relation = vertical_relation or {}

    def to_dict(self) -> dict:
        return {
            "object_id": self.object_id,
            "category": self.category,
            "size": self.size,
            "position": self.position,
            "source_bbox_3d": self.source_bbox_3d,
            "source_centroid_3d": self.source_centroid_3d,
            "bbox_2d": self.bbox_2d,
            "attributes": self.attributes,
            "vertical_relation": self.vertical_relation,
        }

    @staticmethod
    def from_dict(data: dict) -> "MapObject":
        obj = MapObject(
            object_id=data["object_id"],
            category=data["category"],
            size=tuple(data["size"]),
            position=tuple(data.get("position", (0.0, 0.0, 0.0))),
            attributes=data.get("attributes", []),
            vertical_relation=data.get("vertical_relation", {}),
        )
        # 兼容老数据
        if "bbox_2d" in data:
            obj.bbox_2d = tuple(data["bbox_2d"])
        return obj

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
        x, y = position
        w, d = size
        self.bbox_2d = (x, y, x + w, y + d)

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "size": self.size,
            "position": self.position,
            "orientation": self.orientation,
            "bbox_2d": self.bbox_2d,
        }

    @staticmethod
    def from_dict(data: dict) -> "AgentState":
        obj = AgentState(
            agent_id=data["agent_id"],
            size=tuple(data["size"]),
            position=tuple(data["position"]),
            orientation=data["orientation"],
        )
        if "bbox_2d" in data:
            obj.bbox_2d = tuple(data["bbox_2d"])
        return obj

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
        return {
            "map_id": self.map_id,
            "source_type": self.source_type.value,
            "objects": {k: v.to_dict() for k, v in self.objects.items()},
            "grid_map": self.grid_map.tolist() if self.grid_map is not None else None,
            "scene_description": self.scene_description,
            "canvas_size": self.canvas_size,  # 新增
        }

    @staticmethod
    def from_dict(data: dict) -> "MapRepresentation":
        objects = {k: MapObject.from_dict(v) for k, v in data["objects"].items()}
        grid_map = np.array(data["grid_map"]) if data.get("grid_map") is not None else None
        return MapRepresentation(
            map_id=data["map_id"],
            source_type=SourceType(data["source_type"]),
            objects=objects,
            grid_map=grid_map,
            scene_description=data.get("scene_description", ""),
            canvas_size=tuple(data["canvas_size"]) if data.get("canvas_size") is not None else None,  # 新增
        )

    @staticmethod
    def load_from_json(path: str) -> "MapRepresentation":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return MapRepresentation.from_dict(data)

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
