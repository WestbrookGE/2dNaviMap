
-----

## 2D地图中间件：项目技术规格与开发蓝图

### 1\. 项目引言与愿景

本项目旨在构建一个前沿的“2D地图中间件”，作为连接复杂3D世界与大型语言模型（LLM）的核心枢纽。其最终目标是支持一个纯视觉导航大模型的训练，使机器人能够摆脱对预建图的依赖，实现“即到即用”。此中间件的核心任务是将原始的3D场景数据（如高斯泼溅、仿真环境）抽象为结构化的2D地图，并为导航任务的自动化数据标注、路径规划和强化学习提供基础。

### 2\. 核心设计哲学：分层数据与计算

系统架构遵循“关注点分离”原则，将数据和计算划分为三个逻辑层次，确保了系统的清晰性、模块化和可扩展性。

  * **L0 - 原始真值层 (The Ground Truth Layer):**

      * **定义:** 系统的数据基石，完全由外部输入决定，描述“是什么”。
      * **内容:** 场景中所有静态物体的几何信息（3D边界框、质心）和身份信息（类别、ID）。墙体本身也视为一种静态物体。

  * **L1 - 派生知识层 (The Derived Knowledge Layer):**

      * **定义:** 基于L0数据通过计算和推断得出的结构化知识，描述“关系是什么”。
      * **内容:** 物体在2D平面的投影、物体间的垂直空间关系（如“在上”）、全局可通行区域的栅格地图，以及导航本体的实时动态状态。

  * **L2 - 功能接口层 (The Functional API Layer):**

      * **定义:** 系统的能力层，消费L0和L1的数据，对外提供具体的功能和服务。
      * **内容:** 路径规划、碰撞检测、奖励函数计算、为LLM生成结构化输入等。

### 3\. 核心数据结构

#### `MapObject` (地图物体)

代表场景中所有的静态实体，包括家具、障碍物以及墙体。

  * **L0 - 原始属性 (Primitive Attributes):**

      * `object_id: str`: 唯一标识符 (e.g., "desk\_01", "wall\_segment\_01")。
      * `category: str`: 物体类别 (e.g., "桌子", "墙体", "沙发")。
      * `source_bbox_3d: tuple`: 原始3D空间中的3D边界框 `(center_x, center_y, center_z, extent_x, extent_y, extent_z)`。
      * `source_centroid_3d: tuple`: 原始3D空间中的质心坐标 `(x, y, z)`。

  * **L1 - 派生/加工属性 (Derived/Processed Attributes):**

      * `footprint_2d: List[tuple]`: 物体在2D地平面上的投影轮廓，由一系列顶点 `[(x1, y1), (x2, y2), ...]` 定义。
      * `attributes: List[str]`: 描述性标签 (e.g., ["木制", "红色"])，可由外部或LLM提供。
      * `vertical_relation: dict`: 描述垂直空间关系，例如: `{"type": "is_on_top_of", "target_id": "desk_01"}`。

#### `AgentState` (导航本体状态)

代表机器人本体，包含其固有属性和实时可变的状态。

  * **静态属性 (Static Properties):**

      * `agent_id: str`: 本体唯一标识符 (e.g., "robot\_01")。
      * `footprint_polygon: List[Tuple[float, float]]`: 本体自身的2D几何边界/碰撞体积，用于精确碰撞检测。

  * **动态状态 (Dynamic State):**

      * `position: Tuple[float, float]`: 在2D地图中的当前 `(x, y)` 坐标。
      * `orientation: float`: 在2D地图中的当前朝向角度（弧度）。

#### `MapRepresentation` (完整地图表示)

代表整个静态环境的顶层容器。

  * **L0 - 原始属性:**

      * `map_id: str`: 场景唯一标识符。
      * `source_type: Enum`: 场景来源 (e.g., `GAUSSIAN_SPLATting`, `ISAAC_SIM`)。
      * `objects: Dict[str, MapObject]`: 场景中所有静态物体的字典，以 `object_id` 为键。

  * **L1 - 派生/加工属性:**

      * `grid_map: np.ndarray`: 全局2D栅格地图。这是导航和路径规划的核心基础。栅格值可定义为：`0` 代表可通行区域，`1` 代表被障碍占据区域。
      * `scene_description: str`: 由LLM生成的、对整个场景的自然语言总体描述。

### 4\. 功能模块与API

#### 上游场景接口 (Upstream Scene API)

  * `reconstruct_to_middleware(raw_data: any, annotations: dict) -> MapRepresentation`
      * **职责:** 将原始3D场景数据和标注转换为一个完整的、包含L0和L1层信息的 `MapRepresentation` 对象。
      * **核心逻辑:**
        1.  解析 `raw_data` 和 `annotations`，为每个物体（包括墙体）创建 `MapObject` 实例并填充L0属性。
        2.  **调用几何处理器:** 计算每个 `MapObject` 的 `footprint_2d`。
        3.  **调用语义处理器:** 分析所有 `MapObject` 之间的3D位置关系，填充 `vertical_relation`。
        4.  **生成栅格地图:** 基于所有物体的 `footprint_2d`，渲染生成全局 `grid_map`。
        5.  返回最终的 `MapRepresentation` 对象。

#### 下游指令接口 (Downstream Instruction API)

  * `get_llm_structured_input(map_rep: MapRepresentation, agent_state: AgentState) -> str`

      * **职责:** 将地图和机器人状态“翻译”成适合大型语言模型（LLM）输入的JSON格式文本。
      * **核心逻辑:** 提取关键信息，聚合成结构化JSON。输出示例如下：
        ```json
        {
          "scene_description": "这是一个开放式布局的公寓...",
          "robot_state": {
            "position": [1.5, 2.3],
            "orientation_degree": 90
          },
          "visible_objects": [
            {
              "object_id": "red_sofa_1", "category": "沙发", "attributes": ["红色"], "position": [3.0, 4.5]
            },
            {
              "object_id": "monitor_1", "category": "显示器", "relation": {"type": "is_on_top_of", "target": "desk_1"}
            }
          ]
        }
        ```

  * `plan_path(map_rep: MapRepresentation, start_pos: tuple, end_pos: tuple) -> Path`

      * **职责:** 在给定的地图上，规划从起点到终点的最优路径。
      * **核心逻辑:** 在 `map_rep.grid_map` 上运行A\*或其变种算法，返回一个由路径点组成的 `Path` 对象。

#### 环境交互接口 (Environment Interaction API)

  * `check_collision(map_rep: MapRepresentation, agent_state: AgentState) -> bool`

      * **职责:** 提供轻量级、快速的碰撞检测。
      * **核心逻辑:** 将 `agent_state.footprint_polygon` 与 `map_rep.grid_map` 进行相交测试。

  * `calculate_reward(map_rep: MapRepresentation, agent_state: AgentState, reference_path: Path) -> float`

      * **职责:** 为强化学习计算当前状态的奖励值。
      * **核心逻辑:** 综合计算安全奖励（与障碍物距离）、效率奖励（向目标前进的进度）、平滑度奖励（运动轨迹的平滑性）等。

### 5\. 建议的项目结构

```
/2d_map_middleware
|
├── core/
|   └── data_structures.py       # 定义 MapObject, AgentState, MapRepresentation, Path
|
├── processors/
|   ├── geometry_processor.py      # L0->L1: 处理3D投影到2D等几何计算
|   └── semantic_processor.py      # L0->L1: 分析垂直关系等语义信息
|
├── planners/
|   └── astar.py                   # A* 路径规划算法实现
|
├── apis/
|   ├── upstream_api.py            # L2: 实现 reconstruct_to_middleware
|   ├── downstream_api.py          # L2: 实现 get_llm_structured_input, plan_path
|   └── interaction_api.py         # L2: 实现 check_collision, calculate_reward
|
├── utils/
|   ├── visualization.py           # 可视化工具 (绘制地图、物体和本体)
|   └── config.py                  # 加载项目配置
|
├── main.py                        # 主程序入口/端到端示例
|
└── tests/
    ├── test_processors.py
    └── test_apis.py
```

### 6\. 分阶段开发顺序建议

#### **第一阶段：地基搭建 (Foundation)**

1.  **定义数据结构:** 在 `core/data_structures.py` 中完整实现 `MapObject`, `AgentState`, `MapRepresentation` 类及其序列化方法。
2.  **构建可视化工具:** 在 `utils/visualization.py` 中开发一个调试工具，能够读取 `MapRepresentation` 和 `AgentState` 对象，并清晰地绘制出地图、所有物体轮廓以及机器人的位置和朝向。**此为最高优先级，是后续所有开发的基础。**

#### **第二阶段：核心处理模块 (Core Processors)**

1.  **实现几何处理器:** 开发 `processors/geometry_processor.py`，完成将 `source_bbox_3d` 投影到 `footprint_2d` 的核心功能。
2.  **实现语义处理器:** 开发 `processors/semantic_processor.py`，实现 `vertical_relation` 的推断逻辑。
3.  **集成栅格地图生成:** 在上游API的流程中，加入调用处理器并将结果渲染为 `grid_map` 的逻辑。

#### **第三阶段：功能接口与算法集成 (APIs & Algorithms)**

1.  **集成核心算法:** 在 `planners/` 中实现A\*算法。
2.  **封装功能接口:** 按照第四节的定义，在 `apis/` 目录下完整实现所有上游、下游和交互接口的功能。确保API的输入输出与定义一致。

#### **第四阶段：集成测试与完善 (Integration & Refinement)**

1.  **编写单元测试:** 为 `processors` 和 `apis` 中的关键函数编写独立的单元测试。
2.  **进行端到端测试:** 编写 `main.py` 作为一个完整的测试脚本，模拟从加载原始数据 -\> 调用 `reconstruct_to_middleware` -\> 调用所有下游API的完整流程，并使用可视化工具验证每一步结果的正确性。
3.  **迭代优化:** 在真实数据上进行测试，根据结果不断迭代优化各模块的算法和参数。

-----