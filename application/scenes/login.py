from .base import SceneState
            
class LoginSceneState(SceneState):
    """
    登录场景状态类
    """
    def __init__(self, context):
        super().__init__(context)
        self.name_en = "Login"
        self.name_cn = "登录"
        self.targets = ["index_index2_btn", "index_explore_btn"]
        
    def handle(self, founds):
        targets = [
            {"target": "index_index2_btn", "next_scene": 'IndexSceneState'},
            {"target": "index_explore_btn", "next_scene": 'IndexSceneState'},
        ]
        for info in targets:
            if info['target'] in founds:
                self.context.next_state(info['next_scene'])
                break