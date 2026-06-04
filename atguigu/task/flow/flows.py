from dataclasses import dataclass, field
from typing import Dict, List, Any
from atguigu.task.flow.steps import FlowStep, StartedFlowStep


@dataclass(slots=True)
class FlowSlot:
    name: str # 槽位的名字
    type: str = 'any' # 槽位的类型
    label: str = '' # 槽位的标签
    description: str = '' # 槽位的描述

@dataclass (slots=True)
class Flow:
    id: str # 流程的ID
    description: str = '' # 流程的描述
    steps: List[FlowStep] = field(default_factory=list) # 该流程的步骤
    slots: List[FlowSlot] = field(default_factory=list) # 当前流程用到的槽位
    name: str | None = None # 流程的名字

    
    def start_step(self) -> StartedFlowStep | None:
        """
        返回流程的开始步骤
        """

        for step in self.steps:
            if isinstance(step, StartedFlowStep):
            # if step.type = FlowStepType.START:
                return step
            
        return None
    
    def get_step_by_id(self, step_id: str ) -> FlowStep | None:
        """
        根据步骤id查找步骤
        """
        for step in self.steps:
            if step.id == step_id:
                return step
            
        return None

@dataclass(slots=True)
class FlowsList:
    """
    存放两个yaml文件的流程(业务流程以及系统流程)
    """
    flows: List[Flow] = field(default_factory=list)
    slots: Dict[str, FlowSlot] = field(default_factory=dict)

    def get_flow_by_id(self, flow_id) -> Flow | None:
        '''根据流程id获取流程对象'''

        for flow in self.flows:
            if flow.id == flow_id:
                return flow
        
        return None

