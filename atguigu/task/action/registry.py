

from atguigu.task.action.base import Action


class ActionRegistry:
    '''
    动作注册表
    存: 将动作名:动作Action 作为键值对存入字典
    取: 根据动作名获取对应的Action
    '''

    def __init__(self) -> None:
        self._actions: dict[str, Action] = {}

    def register(self, action: Action) -> None:
        self._actions[action.name] = action

    def get(self, name: str) -> Action:
        if name not in self._actions:
            raise KeyError(f"Unknown action '{name}'.")
        return self._actions[name]