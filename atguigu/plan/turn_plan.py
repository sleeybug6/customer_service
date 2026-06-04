
'''
规划器(planner)以及校验器(validator)用到的类型定义
'''

from dataclasses import dataclass, field
from enum import Enum

from atguigu.task.command.command import Command




@dataclass
class TaskTurnPlan:
    commands: list[Command] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict): # 传入的字典应如: {'commands':[{'command':...}, {'command':...}, ...]}
        return cls(commands=[Command.from_dict(command) for command in data['commands']])

@dataclass
class KnowledgeTurnPlan:
    intents:list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict):  # 传入的字典应是{'intents': ['asd', 'abc',....]}
        return cls(intents=data['intents'])


@dataclass
class ChitchatTurnPlan:
    pass




@dataclass
class TurnPlan:

    '''
    用于封装LLM结果的数据模型, 大模型的输入结果类似以下(展示的是三条):
    {
        "task":      { "commands": [{"command": "start_flow", "flow": "refund_request"},...]} 或者 null   
        "knowledge": { "intents": ["refund_policy",...] }     或者null
        "chitchat":  {}      或者null
    }

    '''

    task: TaskTurnPlan | None = None
    knowledge:KnowledgeTurnPlan | None = None
    chitchat:ChitchatTurnPlan | None = None

    @classmethod
    def from_dict(cls, data: dict)  -> 'TurnPlan':
        return cls(
            task=TaskTurnPlan.from_dict(data['task']) if data.get('task') is not None else None,
            knowledge=KnowledgeTurnPlan.from_dict(data['knowledge']) if data.get('knowledge') is not None else None,
            chitchat=ChitchatTurnPlan() if data.get('chitchat') is not None else None
        )



# 校验相关
class ClarifyReason(Enum):

    '''校验不通过时的原因状态码'''

    MISSING_TRACK = "missing_track"
    MULTIPLE_TRACKS = "multiple_tracks"
    MISSING_TASK_COMMANDS = "missing_task_commands"
    MISSING_KNOWLEDGE_INTENT = "missing_knowledge_intent"
    MISSING_FOCUSED_OBJECT = "missing_focused_object"
    OBJECT_REQUIRES_INTENT = "object_requires_intent"
    INVALID_TASK_COMMANDS = "invalid_task_commands"
    MULTIPLE_TASK_FLOWS = "multiple_task_flows"
    UNKNOWN_TASK_FLOW = "unknown_task_flow"



@dataclass
class TurnPlanValidationResult:
    '''校验器返回的数据类型'''

    valid: bool  # Ture表示校验通过
    reason: ClarifyReason | None = None # 不通过的原因状态码