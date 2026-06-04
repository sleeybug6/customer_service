


from typing import Dict, Any, List
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState


"""
内置
action_response: 这个action返回的如:ActionResult().messages:请先选择一个商品，再继续咨询。
action_listen: 这个action返回的:ActionResult()

自定义
action_lookup_order_status
action_lookup_logistics
action_recommend_similar_products


"""


@dataclass
class ActionResult:
    '''动作的产物'''
    messages: List[BotMessage] = field(default_factory=list) # action执行完的消息结果
    slot_updates: Dict[str, Any] = field(default_factory=dict) # 槽位信息
    
class Action(ABC):
    name: str  # action的名字

    @abstractmethod
    async def run(self, states: DialogueState, action_kwargs: Dict[str, Any]) -> ActionResult:
        pass





