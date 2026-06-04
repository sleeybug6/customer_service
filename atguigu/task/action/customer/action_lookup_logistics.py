


from typing import Any, Dict

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.customer.shared import fetch_logistics



class LookupLogisticsAction(Action):
    name = 'action_lookup_logistics'
    async def run(self, states: DialogueState, action_kwargs: Dict[str, Any]) -> ActionResult:
        """
        调用电商平台查询物流信息的接口 ---> 用于给业务任务填槽
        Args:
            states (DialogueState): _description_
            action_kwargs (Dict[str, Any]): _description_

        Returns:
            ActionResult: _description_
        """        
        
        # 准备查询电商平台的接口数据
        order_id = states.active_task.slots['order_number']
        # 发送请求获取返回结果
        logistic_data = await fetch_logistics(order_id)

        # 如果没查到
        if logistic_data is None:
            slot_updates = {
                'logistics_company': '未知',
                'tracking_number': '未知',
                'logistics_status': '暂时无法查询到物流信息, 请稍后再试'

            }
            return ActionResult(slot_updates=slot_updates)


        return ActionResult(
            slot_updates={
                'logistics_company': logistic_data.get('logistics_company', '未知'),
                'tracking_number': logistic_data.get('tracking_number', '未知'),
                'logistics_status': logistic_data.get('status_desc') or logistic_data.get('status') or '未知'
            }
        )