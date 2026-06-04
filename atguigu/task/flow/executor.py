

from dataclasses import asdict

from atguigu.domain.contexts import SystemContext, TaskContext, CollectedSystemContext
from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.base import ActionResult
from atguigu.task.action.runner import ActionCall, ActionRunner
from atguigu.task.flow.flows import FlowsList
from atguigu.task.flow.steps import FlowStep, StartedFlowStep, CollectedFlowStep, ActionFlowStep, EndFlowStep
from atguigu.task.flow.links import FlowStepStaticLink, FlowStepConditionalLink, FlowStepFallbackLink

class FlowExecutor:
    '''
    作用:推进yaml定义的业务任务流程以及系统任务流程
    
    '''

    def __init__(self) -> None:
        pass

    async def run_task(self, states: DialogueState, flows: FlowsList, action_runner: ActionRunner) -> list[BotMessage]:
        """
        作用:推进yaml定义的业务任务流程以及系统任务流程

        Args:
            states (DialogueState): _description_
            flows (FlowsList): _description_
            action_runner (ActionRunner): _description_
        """



        final_messages:list[BotMessage] = []
        while True:

            # 推进流程(flow内部的steps) 直到step的类型type=action的【action_listen、action_response、action_xxxx】
            action_call: ActionCall = self._advance_until_action(states, flows)

            # 获取到了action类型的step
            if action_call.action_name == 'action_listen':
                break

            # 如果是其他action
            else:



                action_result: ActionResult = await action_runner.run(action_call, states)
                
                # ===========测试打印=======================
                # print('='*88)
                # print('Action相关')
                # print(action_call)
                # print(action_result)
                # print('='*88)
                # ===========测试打印=======================

                # 如果这次action有槽位 ---> 添加到当前活跃的业务任务的slots中
                if action_result.slot_updates:
                    states.set_slots(action_result.slot_updates)
                # 机器人的回复信息
                final_messages.extend(action_result.messages)

        
        return final_messages
    
    def _advance_until_action(self, states: DialogueState, flows: FlowsList) -> ActionCall:
        '''
        flow流程推进的核心: 一直往前推进 直到遇到step类型为action
        '''
        while True: 
            
            # 获取当前任务 ---> 可能是系统的任务也可能是业务任务
            current_task: SystemContext | TaskContext  = states.current_active_task() 

            if current_task is None:  # 业务流程和系统流程都走完了
                return ActionCall(action_name='action_listen')

            # 获取流程
            flow = flows.get_flow_by_id(current_task.flow_id)

            # 当前step
            step = flow.get_step_by_id(current_task.step_id) 

            # ============================== 模拟测试 ==============================================
            print(f'当前流程{current_task.flow_id}, 当前step:{step}')
            
            # =====================================================================================

            # 运行当前step
            action_call: ActionCall | None = self._run_step(states, flows, step)

            # 判断step的类型
            # 如果step的类型是action ---> 退出; 否则 ---> 继续往下推
            if action_call:
                return action_call

    def _run_step(self, states: DialogueState, flows: FlowsList, step: FlowStep) -> ActionCall | None:
        """
        运行每一步骤
        Args:
            states (DialogueState): _description_
            flows (FlowsList): _description_
            step (FlowStep): _description_

        Returns:
            ActionCall | None: _description_
        """        
        if isinstance(step, StartedFlowStep):
            return self._run_start_step(states, step)
        
        if isinstance(step, CollectedFlowStep):
            return self._run_collect_step(states, flows, step)
        
        if isinstance(step, ActionFlowStep):
            return self._run_action_step(states, step)
        
        if isinstance(step, EndFlowStep):
            return self._run_end_step(states)
    
    def _run_start_step(self, states: DialogueState, step: StartedFlowStep):
        '''运行开始步骤'''

        self._advance_next_step(states, step)

        return None

    def _run_end_step(self, states: DialogueState):

        # 清空系统任务上下文
        if states.active_system_task:
            states.end_active_system_task()

        # 清空业务任务上下文
        else:
            states.end_active_task()
        
        return None
    
    def _run_action_step(self, states: DialogueState, step: ActionFlowStep) -> ActionCall:
        """

        Args:
            states (DialogueState): _description_
            step (ActionFlowStep): _description_
        """        

        self._advance_next_step(states, step)


        return self._build_action_call(states, step)

    

    def _run_collect_step(self, states: DialogueState, flows:FlowsList, step: CollectedFlowStep):
        
        # 尝试使用fucused object填槽
        self._try_fill_collect_slot(states, step)

        # 判断槽位是否填过了没有
        if states.active_task.slots.get(step.slot_name):
            # 填过了 ---> 代表第二次进来了

            if step.validate:
                # 要校验
                # 如果校验通过 ---> 找下一步
                if self._eval_condition(states, step.validate.condition):
                    self._advance_next_step(states, step)
                    return None
                
                # 校验没通过 ---> 删除填错的槽位并包装ActionCall(action_name='action_response', action_kwargs=)返回
                else:
                    states.remove_slots(step.slot_name)
                    if step.validate.failure_response:
                        return ActionCall(action_name='action_response', action_kwargs=asdict(step.validate.failure_response))
                    else:
                        return ActionCall(action_name='action_response', action_kwargs={'text':'你填写的信息有误,请重新再填'})

            
            else:
                # 无需校验 直接下一步
                self._advance_next_step(states, step)
                return None

        else:
            states.start_active_system_task(CollectedSystemContext(
                flow_id='system_collect_information',
                step_id=flows.get_flow_by_id(flow_id='system_collect_information').start_step().id, 
                slot_name=step.slot_name,
                response=asdict(step.response) # step为业务任务中类型为collect的step
            ))

        
        return None


    def _advance_next_step(self, states: DialogueState, step: FlowStep):
        '''推进到下一个step'''

        # 寻找下一个step
        next_step_id = self._select_next_step(states, step)

        # 更新任务上下文的step_id
        states.current_active_task().step_id = next_step_id


    def _select_next_step(self, states: DialogueState, step: FlowStep) -> str:

        

        for link in step.next:

            if isinstance(link, FlowStepStaticLink):
                return link.target  # 下一个step的ID
            
            if isinstance(link, FlowStepConditionalLink):
                if self._eval_condition(states, link.condition):
                    return link.target
            
            if isinstance(link, FlowStepFallbackLink):
                return link.target
        
        return 'step not exist next'


    def _eval_condition(self, states:DialogueState, condition: str) -> bool:
        
        # condition = context.get('reason') == 'clarification_rejected'
        

        # states.current_active_task()=CannotHandleSystemContext时: {'flow_id':'', 'step_id':'', 'cannot_flow_id':'', 'reason': ''}
        data = {
            'slots': states.active_task.slots,
            'context': asdict(states.current_active_task())
        }
        return bool(eval(condition, {}, data))
    

    def _try_fill_collect_slot(self, states: DialogueState, step: CollectedFlowStep):
        '''使用state中的聚焦对象(卡片)填槽位'''
        
        if states.focused_object is None:
            return None
        

        # states中有fucused object 且槽位合适 ---> 填槽
        if states.focused_object.type == 'order' and step.slot_name == 'order_number':
            states.set_slots({step.slot_name: states.focused_object.id})
        if states.focused_object.type == 'product' and step.slot_name == 'product_id':
            states.set_slots({step.slot_name: states.focused_object.id})

    def _build_action_call(self, states: DialogueState, step: ActionFlowStep) -> ActionCall:

        # 从step中获取action的名字(action_listen/action_repsonse/action_xxx)
        action_name = step.action
        
        # 从step中获取action的args
        action_args = step.args

        # 如果args是字符串 ---> 转成dict 
        # (两个yaml只有系统流程中的system_collect_information的action_response步骤的args才是字符串, 所以此时active_system_task类型一定是CollectedSystemContext)
        if isinstance(action_args, str):
            # action_args='context.response' ---> action_args.split('.')[1]这个式子得到的是'response'
            action_args = asdict(states.active_system_task)[action_args.split('.')[1]]
        
        return ActionCall(action_name=action_name, action_kwargs=action_args)


            



        

