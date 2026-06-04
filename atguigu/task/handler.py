
from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.runner import ActionRunner
from atguigu.task.command.command import Command
from atguigu.task.command.processor import CommandProcessor
from atguigu.task.flow.executor import FlowExecutor
from atguigu.task.flow.flows import FlowsList

class TaskHandler:

    def __init__(self, flows: FlowsList, command_processor:CommandProcessor, action_runner: ActionRunner, flow_executor: FlowExecutor) :

        self.flows = flows
        self.command_processor = command_processor
        self.action_runner = action_runner
        self.flow_executor = flow_executor
        
    

    async def handle(self,  states: DialogueState, commands:list[Command]) -> list[BotMessage]:
        
        # 1. 利用CommandProcessor处理Command命令
        self.command_processor.run(states, commands, self.flows)

        
        # 2. 拿FlowExecutor推进yaml中定义的流程 
        messages: list[BotMessage] = await self.flow_executor.run_task(states, self.flows, self.action_runner)

        
        return messages