from .base import SceneState
            
class Index2SceneState(SceneState):
    """
    町中场景状态类
    """
    def __init__(self, context):
        super().__init__(context)
        self.name_en = "Index2"
        self.name_cn = "町中"
        self.targets = ["index_index2_btn", "index_explore_btn", "battle_preset_btn", "battle_ready_btn"]
        
    def handle(self, founds):
        targets = [
            {"target": "index_index2_btn", "next_scene": 'IndexSceneState'},
            {"target": "index_explore_btn", "next_scene": 'IndexSceneState'},
            {"target": "battle_preset_btn", "next_scene": 'BattleSceneState'},
            {"target": "battle_ready_btn", "next_scene": 'BattleSceneState'},
        ]
        for info in targets:
            if info['target'] in founds:
                self.context.next_state(info['next_scene'])
                break