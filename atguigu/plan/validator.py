


from atguigu.domain.state import DialogueState
from atguigu.plan.turn_plan import TurnPlan
from atguigu.plan.turn_plan import ClarifyReason, TurnPlanValidationResult
from atguigu.task.flow.flows import FlowsList
from atguigu.task.command.command import COMMAND_NAME_TO_CLASS, Command, StartFlowCommand
from atguigu.knowledge.intents import KNOWLEDGE_INTENTS, KnowledgeIntent

class TurnValidator:

    def validate(self, states: DialogueState, turn_plan: TurnPlan, flows: FlowsList) -> TurnPlanValidationResult:
        """
        校验上游LLM得到的轨道结果turn_plan
        Args:
            turn_plan (TurnPlan): 轨道结果
        """

        tracks: list[str] = self._active_tracks(turn_plan)

        # 如果没有名字任何轨道
        if not tracks:
            # 返回校验失败结果
            return TurnPlanValidationResult(valid=False, reason=ClarifyReason.MISSING_TRACK)
        
        # 如果命中多条轨道
        if len(tracks) > 1:
            return TurnPlanValidationResult(valid=False, reason=ClarifyReason.MULTIPLE_TRACKS)
        
        # 获取唯一的轨道
        track = tracks[0]

        # 判断轨道是哪一个
        if track == 'task':
            # 命中业务任务轨道
            return self._validate_task_track(turn_plan, flows)
        
        if track == 'knowledge':
            # 命中信息咨询轨道
            return self._validate_knowledge_track(states, turn_plan, KNOWLEDGE_INTENTS)
        
        
        return TurnPlanValidationResult(valid=True)
    
    def _validate_task_track(self, turn_plan: TurnPlan, flows: FlowsList) -> TurnPlanValidationResult:
        """
        校验业务任务轨道:
        设置四重检验关卡
        1. commands是否为空
        2. commands中命令是否白名单中的四种类型
        3. commands中的start_flow是否存在多个
        4. 判断开启的业务流程ID , 是否在流程清单中

        Args:
            turn_plan (TurnPlan): _description_
            flows (FlowsList): _description_
        """

        # 第一重: commands是否为空
        if not turn_plan.task.commands:
            return TurnPlanValidationResult(valid=False, reason=ClarifyReason.MISSING_TASK_COMMANDS)
        
        
        # 第二重: commands中命令是否白名单中的四种类型
        allowed = COMMAND_NAME_TO_CLASS.values() # 白名单
        # 如果commands中的所有命令都在白名单中才算通过
        if not all([type(command) in allowed for command in turn_plan.task.commands]):
            return TurnPlanValidationResult(valid=False, reason=ClarifyReason.INVALID_TASK_COMMANDS)
        

        # 第三重: commands中的start_flow是否存在多个 (这里只校验了start_flow, 后续可以增加其他flow是否有多个)
        start_flow_cmd = [cmd for cmd in turn_plan.task.commands if isinstance(cmd, StartFlowCommand)]
        if len(start_flow_cmd) > 1:
            return TurnPlanValidationResult(valid=False, reason=ClarifyReason.MULTIPLE_TASK_FLOWS)
        
        
        # 第四重: 判断开启的业务流程ID , 是否在流程清单
        if start_flow_cmd:

            # 根据流程id获取流程清单中的流程，如果获取不到 ---> 说明不在流程清单中
            flow = flows.get_flow_by_id(start_flow_cmd[0].flow)
            if flow is None:
                return TurnPlanValidationResult(valid=False, reason=ClarifyReason.UNKNOWN_TASK_FLOW)
        
        # 校验通过
        return TurnPlanValidationResult(valid=True)
    

    def _validate_knowledge_track(self, states: DialogueState, turn_plan: TurnPlan, knowledge_intents: dict[str, KnowledgeIntent]) -> TurnPlanValidationResult:
        """
        校验知识咨询轨道
        Args:
            states (DialogueState): _description_
            turn_plan (TurnPlan): _description_
            knowledge (dict[str, KnowledgeIntent]): 所有系统支持的意图

        Returns:
            TurnPlanValidationResult: 校验结果
        """

        # 从turn_plan中获取知识咨询轨道的信息
        knowledge_plan = turn_plan.knowledge

        # 如果意图列表为空, 则直接返回校验失败
        if not knowledge_plan.intents:
            return TurnPlanValidationResult(valid=False, reason=ClarifyReason.MISSING_KNOWLEDGE_INTENT)
        
        # 意图列表不为空 ---> 判断列表中的每一个意图是否都在系统支持的意图中
        
        for intent in knowledge_plan.intents:
            
            knowledge_intent = knowledge_intents.get(intent)

            # 如果该意图为系统支持的意图  
            if knowledge_intent:

                # 该意图如果需要对象 
                if knowledge_intent.requires_object:
                    # 但是当前state中没有聚焦对象 或者 聚焦对象的类型不匹配(类型是'order'还是'product')
                    if states.focused_object is None or states.focused_object.type != knowledge_intent.requires_object:
                        return TurnPlanValidationResult(valid=False, reason=ClarifyReason.MISSING_FOCUSED_OBJECT)
                    
            # 如果不为系统支持的意图
            else:
                return TurnPlanValidationResult(valid=False, reason=ClarifyReason.MISSING_KNOWLEDGE_INTENT)

        
        return TurnPlanValidationResult(valid=True)

                
            


        
        
        








        
        

    def _active_tracks(self, turn_plan: TurnPlan) -> list[str]:
        '''数一下命中了几个轨道'''

        tracks = []

        if turn_plan.task is not None:
            tracks.append('task')
        
        if turn_plan.knowledge is not None:
            tracks.append('knowledge')
        
        if turn_plan.chitchat is not None:
            tracks.append('chitchat')
        
        return tracks