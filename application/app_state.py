from enum import Enum, auto

class AppState(Enum):
    STOPPED = auto()
    RUNNING = auto()
    NOT_FOUND_WINDOW = auto()

class YysScene(Enum):
    """
    场景枚举类
    """
    UNKNOW_SCENCE = (auto(), "Unknown Scene", "未知场景")
    LOGIN_SCENCE = (auto(), "Login Scene", "登录界面")
    INDEX_SCENCE = (auto(), "Index Scene", "庭院")
    EXPLORE_SCENCE = (auto(), "Explore Scene", "探索")
    INDEX_2_SCENCE = (auto(), "Index2 Scene", "町中")
    BATTLE_SCENCE = (auto(), "Battle Scene", "战斗中")

    def __new__(cls, value, en_description, cn_description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.en_description = en_description  # 英文描述
        obj.cn_description = cn_description  # 中文描述
        return obj

    def __str__(self):
        # 默认显示英文描述
        return self.en_description

    def get_description(self, language='cn'):
        """
        根据语言返回相应的描述。
        参数:
        - language: 'en' 表示英文, 'cn' 表示中文 (默认)
        """
        if language == 'en':
            return self.en_description
        else:
            return self.cn_description
