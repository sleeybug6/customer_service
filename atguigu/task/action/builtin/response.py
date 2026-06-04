


from typing import Any, Dict

from jinja2 import Template
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.prompts.history_builder import HistoryBuilder
from atguigu.task.action.base import Action, ActionResult
from atguigu.infrastructure.llm import llm

class ActionResponse(Action):
    name = 'action_response'
    async def run(self, states: DialogueState, action_kwargs: Dict[str, Any]) -> ActionResult:
        # 这里的action_kwargs 为{'text':'', 'mode':'', 'prompt':''}

        print('='*88)
        print(action_kwargs)

        text = action_kwargs['text'] # jinja2模板的文本
        mode = action_kwargs.get('mode', 'static')

        rendered_text = self._render_text(states, text) # 使用jinja2模板引擎渲染后的文本

        if mode == 'static':
            # 回复固定文本  不需要调用LLM
            return ActionResult(messages=[BotMessage(text=rendered_text)])

        elif mode == 'rephrase':
            # 需要调用LLM并且将text作为底稿传进去
            prompt = action_kwargs['prompt']
            rephrased_text = await self._call_llm(states, prompt, rendered_text)
            return ActionResult(messages=[BotMessage(text=rephrased_text)])
        
        else:
            # generate模型  只提供prompt调用LLM
            prompt = action_kwargs['prompt']
            generated_text = await self._call_llm(states, prompt)
            return ActionResult(messages=[BotMessage(text=generated_text)])
        

    def _render_text(self, states: DialogueState, text:str) -> str:
        """
        渲染jinja2模板的文本

        Args:
            states (DialogueState): _description_
            text (str): 带有jinja2模板的文本

        Returns:
            str: 渲染后的内容
        """

        template = Template(text)

        result = template.render(
            slots=states.active_task.slots if states.active_task else {},
            context=states.current_active_task()
        )

        return result
    
    async def _call_llm(self, states: DialogueState, prompt:str, redered_text:str='' ) -> str:
        """

        Args:
            states (DialogueState): _description_
            redered_text (str): _description_
            prompt (str): _description_

        Returns:
            str: _description_
        """
        template = PromptTemplate(template=prompt)

        chain = template | llm | StrOutputParser()
        rephrased_text = await chain.ainvoke(
            {
                'history': HistoryBuilder.build(states.current_session().turns[-5:]),
                'user_message': HistoryBuilder._render_user_message(states.pending_turn.user_message),
                'current_response': redered_text
            }
        )

        return rephrased_text
        

if __name__ == "__main__":
    

    text = '提供一下{{slots.order_number}}'
    template = Template(text)
    print(template.render({'slots':{'order_number':'A10001'}}))