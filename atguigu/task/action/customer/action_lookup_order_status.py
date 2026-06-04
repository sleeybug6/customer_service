

from typing import Any, Dict

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.customer.shared import fetch_order, _build_order_summary


class LookupOrderStatusAction(Action):
    """
    调用电商平台查询订单状态的接口
    

    Args:
        Action (_type_): _description_
    """
    name = 'action_lookup_order_status'
    async def run(self, states: DialogueState, action_kwargs: Dict[str, Any]) -> ActionResult:
        
        order_number = states.active_task.slots.get("order_number")
        payload = await fetch_order(order_number)

        if payload is None:
            return ActionResult(slot_updates={
                "order_status": "查询失败",
                "order_summary": "暂时无法查到该订单信息，请稍后再试。",
            })

        return ActionResult(slot_updates={
            "order_status": payload.get("status_desc") or payload.get("status") or "未知",
            "order_summary": _build_order_summary(payload),
        })
        
