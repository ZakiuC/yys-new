from .base import SceneState
            
class ExploreSceneState(SceneState):
    """
    探索场景状态类
    """
    def __init__(self, context):
        super().__init__(context)
        self.name_en = "Explore"
        self.name_cn = "探索"
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