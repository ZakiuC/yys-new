class SceneState:
    """
    场景状态基类
    """
    def __init__(self, context):
        self.name_en = "BaseScene"
        self.name_cn = "场景基类"
        self.targets = []
        self.context = context
        
    def handle(self, founds):
        raise NotImplementedError
