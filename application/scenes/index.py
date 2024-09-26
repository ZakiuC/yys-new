from .base import SceneState
            
class IndexSceneState(SceneState):
    """
    庭院场景状态类
    """
    def __init__(self, context):
        super().__init__(context)
        self.name_en = "Index"
        self.name_cn = "庭院"
        self.targets = ["explore_tag", "index2_index_btn"]
        
    def handle(self, founds):
        targets = [
            {"target": "explore_tag", "next_scene": 'ExploreSceneState'},
            {"target": "index2_index_btn", "next_scene": 'Index2SceneState'},
        ]
        for info in targets:
            if info['target'] in founds:
                self.context.next_state(info['next_scene'])
                break