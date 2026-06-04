


from atguigu.domain.contexts import TaskContext, StartedSystemContext, InterruptedSystemContext, CanceledSystemContext, ResumedSystemContext
from atguigu.domain.state import DialogueState
from atguigu.task.command.command import CancelFlowCommand, Command, StartFlowCommand, SetSlotsCommand, ResumeFlowCommand
from atguigu.task.flow.flows import FlowsList


class CommandProcessor:
    '''
    命令处理器
    '''

    def __init__(self) -> None:
        pass

    def run(self, states: DialogueState, commands:list[Command], flows: FlowsList):
        
        # 遍历command
        for cmd in commands:

            # 处理每一个command
            self._apply(states, cmd, flows)
    
        

    def _apply(self, states: DialogueState, cmd: Command, flows: FlowsList):
        

        if isinstance(cmd, StartFlowCommand):
            self._handle_start_flow(states, cmd, flows)

        elif isinstance(cmd, SetSlotsCommand):
            self._handle_set_slots(states, cmd)
        
        elif isinstance(cmd, ResumeFlowCommand):
            self._handle_resume_flow(states, cmd, flows)

        elif isinstance(cmd, CancelFlowCommand):
            self._handle_cancel_flow(states, flows)
        
        else:
            pass

    

    def _handle_start_flow(self, states: DialogueState, cmd: StartFlowCommand, flows: FlowsList):
        """
        要开启的业务任务的ID: cmd.flow
        要开启的业务任务的name: _readable_flow_name()
        Args:
            states (DialogueState): _description_
            cmd (StartFlowCommand): _description_
            flows (FlowsList): _description_
        """

        # 清空系统流程
        states.end_active_system_task()
        # 判断开启的流程是否为系统流程
        if cmd.flow.startswith('system_'):
            raise ValueError(f'不能开启系统流程:{cmd.flow}')

        # 获取流程对象
        target_flow = flows.get_flow_by_id(cmd.flow)

        # 开启新业务任务之前判断先当前有没有业务任务
        active_task = states.active_task
        # 如当前有业务任务
        if active_task is not None:
            # 如果要开启的新业务就是当前业务
            if cmd.flow == states.active_task.flow_id :
                return 
            
            # 要开启的新业务不为当前任务 ---> 打断当前任务
            # 中断别人
            states.interrupted_active_task()
            interrupted_flow_id:str = active_task.flow_id # 中断老业务的流程ID
            interrupted_flow_name:str = CommandProcessor._readable_flow_name(active_task.flow_id, flows)  # 中断老业务的流程名字
            

            # 检查自己是否在栈中
            # 如果栈中没有  ---> 需要开启新业务
            if not states.resumed_active_task(cmd.flow):
                started_flow_id = cmd.flow 
                started_flow_name = CommandProcessor._readable_flow_name(cmd.flow, flows)
                states.start_active_task(TaskContext(flow_id=cmd.flow, step_id=target_flow.start_step().id))

            # 已经在栈中(表示上面的resumed_active_task返回了True, 并且已经从栈中取出来作为了states.active_task)
            else:
                started_flow_id = cmd.flow 
                started_flow_name = CommandProcessor._readable_flow_name(cmd.flow, flows)
                
            # 引出中断系统流程(过场白)
            CommandProcessor._activate_interrupt_system_task(
                states=states,
                flows=flows,
                interrupted_flow_id=interrupted_flow_id,
                interrupted_flow_name=interrupted_flow_name,
                started_flow_id=started_flow_id,
                started_flow_name=started_flow_name
            )


            return 
      

        # 当前没有业务任务(即states.active_task为None)
        # 如果栈中有你, 不要用重复开，只要从栈中恢复
        if states.resumed_active_task(cmd.flow):
            # 业务任务从栈中恢复同时启动以下系统的恢复流程开场白
            CommandProcessor._activate_resume_system_task(
                states=states,
                flows=flows,
                resumed_flow_id=target_flow.id,
                resumed_flow_name=CommandProcessor._readable_flow_name(target_flow.id, flows)
            )
            return 
        
        # 1. 栈中没有你，开启业务任务
        states.start_active_task(TaskContext(flow_id=cmd.flow, step_id=target_flow.start_step().id))

        # 2. 激活系统流程任务 
        CommandProcessor._activate_start_system_task(states, flows, cmd.flow, CommandProcessor._readable_flow_name(cmd.flow, flows))
        

    def _handle_set_slots(self, states: DialogueState, cmd: SetSlotsCommand):
        if states.active_task is not None:
            states.set_slots(cmd.slots)

    def _handle_resume_flow(self, states: DialogueState, cmd: ResumeFlowCommand, flows: FlowsList):
        # ===== 第一步:确定要恢复哪个流程 =====
        if cmd.flow is not None:
            # 指名恢复:用户明确说了恢复哪个
            target_flow = flows.get_flow_by_id(cmd.flow)
            if target_flow is None:
                raise ValueError(f'流程ID不合法:{cmd.flow}')
            target_flow_id = target_flow.id
            target_flow_name = target_flow.name
        else:
            # 不指名恢复:用户只说了继续刚才的.... -> 取栈顶
            if not states.paused_tasks:
                return
            top_paused = states.paused_tasks[-1] # 取栈顶
            target_flow_id = top_paused.flow_id
            target_flow_name = CommandProcessor._readable_flow_name(top_paused, flows)

        # ===== 第二步:按"当前有没有活跃任务"恢复 =====
        active_task = states.active_task
        
        if active_task is not None:

            # 判断要恢复的任务流程ID是否和正在执行的任务流程ID一样
            if target_flow_id == active_task.flow_id:
                return
            
            # 当前有正在执行的任务但是又想恢复target_flow_id对应的任务 ---> 需先打断当前任务
            states.interrupted_active_task() # 将当前正在执行的任务入栈
            interrupted_flow_id = active_task.flow_id
            interrupted_flow_name:str = CommandProcessor._readable_flow_name(interrupted_flow_id, flows)

            if not states.resumed_active_task(target_flow_id): # target_flow恢复失败了(target_flow没有在栈中)
                states.resumed_active_task()  # 恢复之前被压入栈的active_task
                print('当前有active_task, 但是要恢复的任务恢复失败了')
                return 
            
            print('当前有active_task但是又要恢复paused_task中的业务任务---恢复成功')
            # 因为当前有active_task但是又要恢复paused_task中的业务任务 ---> 引入系统打断开场白
            self._activate_interrupt_system_task(
                states=states,
                flows=flows,
                interrupted_flow_id=interrupted_flow_id,
                interrupted_flow_name=interrupted_flow_name,
                started_flow_id=target_flow_id,
                started_flow_name=target_flow_name
            )
        
        # 当前没有正在执行的活跃任务
        else:
            if not states.resumed_active_task(target_flow_id): # 如果恢复失败
                return
            
            # 如果恢复成功了 ---> state中的active_task就会变成target_flow
            # 引入系统流程中的恢复开场白
            CommandProcessor._activate_resume_system_task(
                states=states,
                flows=flows,
                resumed_flow_id=target_flow_id,
                resumed_flow_name=target_flow_name
            )
            
            




    def _handle_cancel_flow(self, states: DialogueState, flows: FlowsList):
        """
        取消当前激活的业务任务
        Args:
            states (DialogueState): _description_
            cmd (CancelFlowCommand): _description_

        Returns:
            _type_: _description_
        """
        
        # 获取当前激活任务
        active_task = states.active_task

        if active_task is None:
            return 
        
        # 取消当前激活的任务
        states.cancel_active_task()

        # 引入系统取消任务的开场白
        CommandProcessor._activate_cancel_system_task(
            states=states,
            flows=flows,
            cancel_flow_id=active_task.flow_id,
            cancel_flow_name=CommandProcessor._readable_flow_name(active_task.flow_id, flows)
        )
        


    @staticmethod
    def _readable_flow_name(flow_id:str, flows:FlowsList) -> str:
        '''根据流程ID获取流程名字'''

        flow = flows.get_flow_by_id(flow_id)

        return flow.name if flow else flow_id # type: ignore
    
    @staticmethod
    def _activate_start_system_task(states: DialogueState, flows: FlowsList, started_flow_id: str, started_flow_name: str):
        """
        激活开始系统任务的开场白

        Args:
            states (DialogueState): _description_
            flows (FlowsList): 所有流程信息 ---> 这里用于获取系统流程(根据流程id:'system_task_started')
            started_flow_id (str): 要开始的业务流程ID
            started_flow_name (str): 要开始的业务流程名字
        """

        # 获取系统流程中的开始流程
        flow = flows.get_flow_by_id('system_task_started')

        # 开启开始的系统流程
        states.start_active_system_task(StartedSystemContext(
            flow_id=flow.id, 
            step_id=flow.start_step().id, 
            started_flow_id=started_flow_id, 
            started_flow_name=started_flow_name
        ))

        
    

    @staticmethod
    def _activate_interrupt_system_task(
        states: DialogueState, 
        flows: FlowsList,  
        interrupted_flow_id:str , # 中断老业务的流程ID
        interrupted_flow_name:str ,  # 中断老业务的流程名字
        started_flow_id:str , # 开始新业务的流程ID
        started_flow_name:str , # 开始新业务的流程名字
    ):
        '''激活系统流程中打断流程的开场白'''

        
        # 获取系统流程中的打断流程
        flow = flows.get_flow_by_id('system_task_interrupted')


        states.start_active_system_task(InterruptedSystemContext(
            flow_id=flow.id,
            step_id=flow.start_step().id,
            interrupted_flow_id=interrupted_flow_id,
            interrupted_flow_name=interrupted_flow_name,
            started_flow_id=started_flow_id,
            started_flow_name=started_flow_name

        ))


    @staticmethod
    def _activate_resume_system_task(states: DialogueState, flows: FlowsList, resumed_flow_id: str, resumed_flow_name:str):
        '''系统流程中的恢复任务开场白'''
        
        flow = flows.get_flow_by_id('system_task_resumed')

        states.start_active_system_task(ResumedSystemContext(
            flow_id=flow.id,
            step_id=flow.start_step().id,
            resumed_flow_id=resumed_flow_id,
            resumed_flow_name=resumed_flow_name
        ))
        
        pass 
    
    @staticmethod
    def _activate_cancel_system_task(states: DialogueState, flows: FlowsList, cancel_flow_id: str, cancel_flow_name: str):
        
        flow = flows.get_flow_by_id('system_task_canceled')

        states.start_active_system_task(CanceledSystemContext(
            flow_id=flow.id,
            step_id=flow.start_step().id,
            canceled_flow_id=cancel_flow_id,
            canceled_flow_name=cancel_flow_name
        ))








    