from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class Command:
    command: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Command': 
        clz = COMMAND_NAME_TO_CLASS.get(data['command'])
        if clz:
            return clz(**data)
        
        return cls(**data)


@dataclass
class StartFlowCommand(Command):
    flow: str  # 开启新业务流程的流程ID(LLM给的，而LLM根据你提供可用流程清单:available_flow_json)


@dataclass
class SetSlotsCommand(Command):
    slots: Dict[str, Any]  # 如{'order_number':'A20260...'} LLM给你的填充槽位信息, 你给LLM的流程信息(available_flow_json)中会有槽位信息


@dataclass
class CancelFlowCommand(Command):
    pass  # 只支持取消当前的业务任务

@dataclass 
class ResumeFlowCommand(Command):
    flow: str | None = None   # 恢复指定的业务流程或者当前活跃的业务流程(LLM给你的, 而LLM根据你提供interrupted_task_json)


COMMAND_NAME_TO_CLASS = {
    'start_flow': StartFlowCommand,
    'resume_flow': ResumeFlowCommand,
    'cancel_flow': CancelFlowCommand,
    'set_slots': SetSlotsCommand
}

if __name__ == "__main__":
    if type(CancelFlowCommand(command='xx')) in COMMAND_NAME_TO_CLASS.values():
    # if CancelFlowCommand(command='xx',flow='xx') in COMMAND_NAME_TO_CLASS.values():
        print(123)
    print(type(CancelFlowCommand(command='a')) in COMMAND_NAME_TO_CLASS.values())
    if isinstance(ResumeFlowCommand(command='xx',flow='xx'), tuple(COMMAND_NAME_TO_CLASS.values())):
        print(666)

    