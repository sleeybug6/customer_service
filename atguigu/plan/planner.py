

import json
from dataclasses import asdict
from typing import Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from atguigu.domain.state import DialogueState
from atguigu.infrastructure.llm import llm
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.prompts.loader import load_prompt
from atguigu.prompts.history_builder import HistoryBuilder
from atguigu.task.flow.flows import Flow, FlowsList
from atguigu.plan.turn_plan import TurnPlan


class TurnPlanner:
    '''
    意图分析器
    根据任务的自然语言调用LLM ---> 分析属于哪条轨道(知识问答、闲聊、业务任务)
    '''
    def __init__(self):
        pass

    async def predict(self, states: DialogueState, flows: FlowsList, knowledge_intents:dict[str, KnowledgeIntent]) -> TurnPlan:
   
        """
        根据当前状态(包括会话历史、用户当前发送的消息等)使用LLM判断走哪个轨道

        Args:
            states (DialogueState): 当前状态

        Returns:
            TurnPlan: 分析得到的轨道结果
        """

        # 构建提示词
        inputs_prompt = self._build_inputs_prompt(states, flows, knowledge_intents)

        # 调用LLM
        return await self._predict_from_inputs_prompt(inputs_prompt)


    
    def _build_inputs_prompt(self, states: DialogueState, flow_list: FlowsList, knowledge_intents:dict[str, KnowledgeIntent]) -> dict[str, Any]:
        """
        构建提示词模板中所需变量的字典, 

        Args:
            states (DialogueState): 对话状态聚合根
            flow_list (FlowsList): 流程信息

        Returns:
            dict[str, Any]: 字典的key为字段名, value为字段内容
        """


        # 1. 当前用户发来的消息
        user_message: str = HistoryBuilder._render_user_message(states.pending_turn.user_message)

        # 2. 历史消息 (当前session的turns: 最近10轮)
        current_conversation: str = HistoryBuilder.build(states.current_session().turns[-10:])

        # 3. 当前激活的任务
        active_task_json = json.dumps(states.active_task.to_dict(), ensure_ascii=False) if states.active_task is not None else None

        # 4. 中断被挂起的任务
        interrupted_tasks_json = json.dumps([paused_task.to_dict() for paused_task in states.paused_tasks], ensure_ascii=False)
        
        # 5. 当前聚焦对象
        focused_object_json= json.dumps(states.focused_object.to_dict(), ensure_ascii=False) if states.focused_object is not None else None

        # 6. 系统支持的所有流程清单
        available_flows_json = json.dumps({'flows':[{k:v for k,v in asdict(flow).items() if k != 'steps'} for flow in flow_list.flows]}, ensure_ascii=False)    


        # 7. 系统支持的所有知识意图
        knowledge_intents_json = json.dumps([{'id':intent.id, 'description':intent.description} for intent in knowledge_intents.values()], ensure_ascii=False)






        return {
            'user_message': user_message,
            'current_conversation': current_conversation,
            'active_task_json': active_task_json,
            'interrupted_tasks_json': interrupted_tasks_json,
            'focused_object_json': focused_object_json,
            'available_flows_json': available_flows_json,
            'knowledge_intents_json': knowledge_intents_json,
        }


    async def _predict_from_inputs_prompt(self, inputs_prompts:dict[str, Any]) -> TurnPlan:

        """
        1. 加载提示词模板
        2. 填入对应的值

        Args:
            states (DialogueState): _description_
        """

        # 加载提示词模板
        prompt_template = load_prompt('turn_plan')
        template = PromptTemplate.from_template(template=prompt_template, template_format='jinja2')

        # 构建chain
        chain = template | llm | JsonOutputParser()
        

        
        # 调用LLM获取结果
        llm_response:dict = await chain.ainvoke(inputs_prompts)


        print('planner调用llm结果:', llm_response)
        # 封装成TurnPlan返回
        return TurnPlan.from_dict(llm_response)


if __name__ == "__main__":
    # s = '{"task": null, "knowledge": null, "chitchat": {}}'
    # import json
    # s_dict = json.loads(s)
    # print(s_dict)
    # tp = TurnPlan.from_dict(s_dict)
    # print(tp)
    # print(s_dict[''])
    llm_response = {'task': None, 'knowledge': {'intents': ['refund_policy']}, 'chitchat': None}
    print(TurnPlan.from_dict(llm_response))






        
    
        