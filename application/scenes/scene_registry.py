from .unknown import UnknownSceneState
from .login import LoginSceneState
from .index import IndexSceneState
from .index2 import Index2SceneState
from .explore import ExploreSceneState
from .battle import BattleSceneState
# 导入其他场景状态类

# 定义场景状态类字典
scene_state_classes = {
    'UnknownSceneState': UnknownSceneState,
    'LoginSceneState': LoginSceneState,
    'IndexSceneState': IndexSceneState,
    'Index2SceneState': Index2SceneState,
    'ExploreSceneState': ExploreSceneState,
    'BattleSceneState': BattleSceneState
}
