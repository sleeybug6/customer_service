


from typing import Any, Dict

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult


class ActionListener(Action):
    name = 'action_listen'
    async def run(self, states: DialogueState, action_kwargs: Dict[str, Any]) -> None:
        

        pass