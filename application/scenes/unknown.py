from .base import SceneState

class UnknownSceneState(SceneState):
    """
    未知场景状态类
    """
    def __init__(self, context):
        super().__init__(context)
        self.name_en = "Unknown"
        self.name_cn = "未知"
        self.targets = ["login_tag", "login_enter_btn", "index_index2_btn", "index_explore_btn", "explore_tag", "index2_index_btn"]
        
        
    def handle(self, founds):
        targets = [
            {"target": "login_tag", "next_scene": 'LoginSceneState'},
            {"target": "login_enter_btn", "next_scene": 'LoginSceneState'},
            {"target": "index_index2_btn", "next_scene": 'IndexSceneState'},
            {"target": "index_explore_btn", "next_scene": 'IndexSceneState'},
            {"target": "explore_tag", "next_scene": 'ExploreSceneState'},
            {"target": "index2_index_btn", "next_scene": 'Index2SceneState'},
        ]
        for info in targets:
            if info['target'] in founds:
                self.context.next_state(info['next_scene'])
                break