from dataclasses import asdict
import time

from atguigu.chitchat.handler import ChitchatHandler
from atguigu.clarifyer.responser import ClarifyResponser
from atguigu.domain.contexts import CannotHandleSystemContext
from atguigu.domain.messages import MessageType, ProcessResult, UserMessage, BotMessage
from atguigu.domain.state import DialogueState
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.turn_plan import ClarifyReason, TurnPlan, TurnPlanValidationResult
from atguigu.task.command.command import Command, SetSlotsCommand
from atguigu.task.flow.flows import FlowsList
from atguigu.task.flow.steps import CollectedFlowStep
from atguigu.task.handler import TaskHandler
from atguigu.plan.validator import TurnValidator

class DialogueEngine:
    """

    调度中心(只负责协调各个组件， 真正工作的是各个组件)

    """

    def __init__(self, turn_planner: TurnPlanner, turn_validator: TurnValidator, clarify_responser: ClarifyResponser,  task_handler: TaskHandler, knowledge_handler: KnowledgeHandler, chitchat_handler: ChitchatHandler) -> None:
        self.turn_palnner = turn_planner
        self.turn_validator = turn_validator  # 校验器
        self.clarify_responser = clarify_responser  # 意图澄清器
        self.task_handler = task_handler   # 负责处理业务任务轨道
        self.knowledge_handler = knowledge_handler # 负责处理信息咨询轨道
        self.chitchat_handler = chitchat_handler  # 负责处理闲聊轨道
    

    async def handle_dialogue(self, dialogue_state: DialogueState, user_message: UserMessage) -> ProcessResult:
        """
        引擎处理对话的顶层入口

        Args:
            dialogue_state (DialogueState): 该用户的对话状态 --- 取自customer_service数据库
            user_message (UserMessage): 用户当前发来的消息

        Returns:
            ProcessResult: 处理结果(包含了机器人回复的消息)
        """
        

        # 1. 开启业务session
        self._prepare_session(dialogue_state)

        # 2. 开启turn
        self._begin_turn(dialogue_state, user_message)
        

        # 3. 判断消息类型
        # 3.1 文本消息类型
        if user_message.type == MessageType.TEXT:
            bot_messages: list[BotMessage] = await self._handle_text_msg(dialogue_state, self.turn_palnner, self.task_handler, self.knowledge_handler)
           

        # 3.2 对象消息类型
        else:

            dialogue_state.set_focused_object(user_message.object)
            bot_messages: list[BotMessage] = await self._handle_obj_msg(dialogue_state, self.task_handler.flows)
            
            
        # 4. 更新state中pendding_turn中的bot_messages
        dialogue_state.pending_turn.bot_messages.extend(bot_messages)

        # 5. 提交turn 
        dialogue_state.commit_turn()

    
        # ============================== 模拟测试 ==============================================
        print('*'*88, '\n')                                                                     
        print('当前激活的任务:\n',dialogue_state.active_task)
        print('当前激活的系统流程:\n', dialogue_state.active_system_task)
        print('当前挂起的任务:\n', dialogue_state.paused_tasks)
        print()
        print('*'*88, '\n')
        
        # =====================================================================================



        
        return ProcessResult(
            sender_id=user_message.sender_id,
            message_id=user_message.message_id,
            bot_messages=bot_messages
        )

    def _prepare_session(self, states:DialogueState):
        

        # 获取当前session是否存在
        current_session = states.current_session()
        if current_session is None:
            # 不存在则创建session
            states.start_session()
            return  
        
        # 检查当前session是否可用(如是否超时), 如果不可用则创建session
        now = time.time()
        if (now-current_session.last_activity_at) > 60*60: # 超时了一小时以上
            # 如果当前的session超时了 ---> 则关闭该session 并创建新的
            states.close_session()
            states.reset_running_state_for_new_session()
            states.start_session()
        else:
            # 当前session有效就直接更新其的last_activity_at即可
            current_session.last_activity_at = now
    

    def _begin_turn(self, states: DialogueState, user_message: UserMessage):
        
        states.begin_turn(user_message)
    

    async def _handle_text_msg(self, states: DialogueState, turn_planner: TurnPlanner, task_handler: TaskHandler, knowledge_handler:KnowledgeHandler) -> list[BotMessage]:
        """
        处理文本类型的消息

        Args:
            states (DialogueState): _description_
            turn_planner (TurnPlanner): _description_
        """
        
        # 1. 调用LLM进行意图识别
        turn_plan: TurnPlan = await turn_planner.predict(states=states, flows=task_handler.flows, knowledge_intents=knowledge_handler.knowledge_intents)
     

        # 2. 校验 ---> 得到校验结果validated
        validated: TurnPlanValidationResult = self.turn_validator.validate(states, turn_plan, task_handler.flows)
        print(turn_plan)
        print(validated)

        # 2.1 如果校验不通过 ---> 则使用澄清器
        if not validated.valid:
            # states.active_system_task(CannotHandleSystemContext(
            #     flow_id='system_cannot_handle',
            #      # TODO

            # ))
            return await self.clarify_responser.respond(states, validated.reason)
        

        # 2.2 如果校验通过 ---> 执行对应轨道进行处理
        
        if turn_plan.task is not None:
            return await self.task_handler.handle(states, turn_plan.task.commands)
        elif turn_plan.knowledge is not None:
            return await self.knowledge_handler.handle(states, turn_plan.knowledge.intents)
        else:
            return await self.chitchat_handler.handle(states)
        



    async def _handle_obj_msg(self, states: DialogueState, flows: FlowsList) -> list[BotMessage]:
        # 将对象解析成命令(SetSlotsCommand)
        commands: list[Command] = self._resolve_object_command(states.pending_turn.user_message, states, flows)

        # 判断commands是否有(有的话表示刚好这个对象是流程所需要的) ---> 继续后续流程即可
        if commands:
            print('开启了SetSlotsCommand')
            return await self.task_handler.handle(states, commands)
        
        # commands没有但是业务流程存在, 让原来流程继续
        if states.active_task is not None:
            print('发来的对象跟当前业务无关, 无视了')
            return await self.task_handler.handle(states, commands)

        # 业务流程不存在
        return await self.clarify_responser.respond(states=states, reason=ClarifyReason.OBJECT_REQUIRES_INTENT)

        



    
    def _resolve_object_command(self, user_message: UserMessage, states: DialogueState, flows: FlowsList) -> list[Command]:
        
        # 获取对象消息
        user_obj = user_message.object

        # 获取对象消息的类型(order 还是 product)
        obj_type = user_obj.type

        # 判断对象的类型
        if obj_type == 'order': # 如果是order类型的对象，就应将对象id填到order_number上
            if self._flow_has_unfilled_collect_slot(states, flows, 'order_number'):
                return [SetSlotsCommand(command='set_slots', slots={'order_number':user_obj.id})]

            return []

        if obj_type == 'product':
            if self._flow_has_unfilled_collect_slot(states, flows, 'product_id'):
                return [SetSlotsCommand(command='set_slots', slots={'product_id':user_obj.id})]
            return []
        
        return []
    
    def _flow_has_unfilled_collect_slot(self, states: DialogueState, flows: FlowsList, slot_name: str) -> bool:
        
        # 获取当前活跃任务
        active_task = states.active_task

        # 判断是否有活跃任务
        if active_task is None:
            return False
        
        # 当前活跃任务的flow_id
        flow_id = active_task.flow_id
        flow = flows.get_flow_by_id(flow_id)
        if flow is None:
            return False
        
        # 判断该流程中当前槽位是否已经填过了 --- 流程中slot_name这个槽位没有填过或者压根没有slot_name这个槽位，get(slot_name)都会返回None
        if active_task.slots.get(slot_name):
            print('当前槽位已经填过了')
            return False
        

        print('=============================', slot_name)
        # 要是没填过
        for step in flow.steps:

            # 如果该流程步骤中有该槽位
            if isinstance(step, CollectedFlowStep) and step.slot_name == slot_name:
                # print('CollectedFlowStep')
                return True
            
        # 流程步骤中压根没有这个槽位也返回False
        return False

   
        
if __name__ == "__main__":
    a = MessageType('text')
    
    print(type(a))
    if a in MessageType.TEXT:
        print(123)