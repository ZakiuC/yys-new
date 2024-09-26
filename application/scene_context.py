from .scenes.unknown import UnknownSceneState
from .scenes.scene_registry import scene_state_classes
from tools.logger import LogManager

class SceneContext:
    def __init__(self):
        self.logger = LogManager(name="scene_context")
        self.state = UnknownSceneState(self)
        self.last_state = UnknownSceneState(self)

    def next_state(self, new_state):
        next_scene_class = scene_state_classes.get(new_state)
        if not next_scene_class:
            self.logger.error(f"无法找到场景状态类：{new_state}")
            return
        next_state_instance = next_scene_class(self)
        self.last_state = self.state
        self.state = next_state_instance
        self.logger.info(f"场景切换：从 {self.last_state.name_cn} 到 {self.state.name_cn}")

    def prev_state(self):
        backup_state = self.last_state
        self.last_state = self.state
        self.state = backup_state
        self.logger.info(f"场景切换：从 {self.last_state.name_cn} 到 {self.state.name_cn}")
        
    def update(self, founds):
        self.state.handle(founds)
