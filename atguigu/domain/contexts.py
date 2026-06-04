from typing import Dict, Any
from dataclasses import dataclass, field, asdict


@dataclass(slots=True)
class TaskContext:
    '''
    业务任务的上下文
    '''
    flow_id:str # 业务流程的流程ID
    step_id:str | None = None # 业务流程下步骤ID
    slots:Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data:Dict[str, Any]) -> 'TaskContext':
        return cls(
            flow_id=data['flow_id'],
            step_id=data.get('step_id'),
            slots=dict(data.get('slots',{}))
        )


@dataclass(slots=True)
class SystemContext:
    '''
    系统流程上下文
    '''
    flow_id:str # 系统流程的流程ID(如system_task_started)
    step_id:str | None = None # 系统流程的步骤ID(如start)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data:Dict[str, Any]) -> 'SystemContext':
        clz = FLOW_ID_TO_CONTEXT_CLASS[data['flow_id']]
        return clz(**data)

@dataclass(slots=True)
class StartedSystemContext(SystemContext):
    started_flow_id:str = '' # 开启具体某一业务流程的流程ID 如order_status_query
    started_flow_name:str = '' # 开启具体某一业务流程的名字 如订单状态查询


@dataclass(slots=True)
class InterruptedSystemContext(SystemContext):
    interrupted_flow_id:str = '' # 中断老业务的流程ID
    interrupted_flow_name:str = ''  # 中断老业务的流程名字
    started_flow_id:str = '' # 开始新业务的流程ID
    started_flow_name:str = '' # 开始新业务的流程名字

@dataclass(slots=True)
class ResumedSystemContext(SystemContext):
    resumed_flow_id:str = '' # 恢复业务的流程ID
    resumed_flow_name:str = '' # 恢复业务的流程名字

@dataclass(slots=True)
class CollectedSystemContext(SystemContext):
    slot_name: str = ""  # 收集的槽位名：order_number(未来扩展渲染的时候能用到、点击卡片的时候，槽位的名字能做判断)
    response: Dict[str, Any] = field(default_factory=dict)  # {"text":"请告诉我你的订单号"} （响应输出的内容）
@dataclass(slots=True)
class CanceledSystemContext(SystemContext):
    canceled_flow_id:str = ''
    canceled_flow_name:str = ''

@dataclass(slots=True)
class CannotHandleSystemContext(SystemContext):
    cannot_flow_id: str = ''
    reason: str = ''








FLOW_ID_TO_CONTEXT_CLASS: Dict[str, Any] = {
    "system_task_started": StartedSystemContext,
    "system_task_resumed": ResumedSystemContext,
    "system_collect_information": CollectedSystemContext,
    "system_task_interrupted": InterruptedSystemContext,
    "system_task_canceled": CanceledSystemContext,
    'system_cannot_handle': CannotHandleSystemContext
}
        
