from enum import Enum, auto
from .base import SceneState


class BattleState(Enum):
    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _, description_en=None, description_cn=None):
        self._description_en = description_en
        self._description_cn = description_cn

    BATTLE_READY = (auto(), "ready", "准备")
    BATTLE_DOING = (auto(), "progress", "进行中")
    BATTLE_END = (auto(), "completed", "结束")

    @property
    def description_en(self):
        return self._description_en

    @property
    def description_cn(self):
        return self._description_cn

    
class BattleSceneState(SceneState):
    """
    战斗场景状态类
    """
    def __init__(self, context):
        super().__init__(context)
        self.name_en = "Battle"
        self.name_cn = "战斗"
        self.targets = []
        # todo: 战斗场景的状态机, 包括战斗准备，战斗中，战斗结算等状态
        self.is_over = False
        self.battle_state = BattleState.BATTLE_READY
        self.workflow = {"battle_ready_btn": BattleState.BATTLE_READY,
                         "battle_preset_btn": BattleState.BATTLE_READY,
                         "battle_auto_btn": BattleState.BATTLE_DOING,
                         "battle_clickContinue_tag": BattleState.BATTLE_END}
        
    def handle(self, founds):
        if self.is_over:
            self.name_en = "Battle"
            self.name_cn = "战斗"
            targets = [
            ]
            # 找到目标后，切换到相应的场景
            for info in targets:
                if info['target'] in founds:
                    self.context.next_state(info['next_scene'])
                    break
        else:
            # 战斗结束返回上一场景
            if self.battle_state == BattleState.BATTLE_END:
                self.context.prev_state()
            else:  
                self.targets = list(self.workflow.keys())
                for tag, state in self.workflow.items():
                    if tag in founds:
                        self.battle_state = state
                        self.name_en = "Battle | " + state.description_en
                        self.name_cn = "战斗 | " + state.description_cn
                    