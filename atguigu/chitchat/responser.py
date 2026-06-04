
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from atguigu.domain.messages import UserMessage, BotMessage
from atguigu.domain.state import Turn
from atguigu.prompts.history_builder import HistoryBuilder
from atguigu.prompts.loader import load_prompt
from atguigu.infrastructure.llm import llm

class ChitchatResponser:

    async def respond(self, user_message: UserMessage, recent_turns: list[Turn]) -> list[BotMessage]:

        # 获取用户消息字符串
        user_message_str = HistoryBuilder._render_user_message(user_message)

        # 获取历史消息字符串
        history = HistoryBuilder.build(recent_turns)

        # 获取提示词模板
        template = PromptTemplate.from_template(template=load_prompt('chitchat_respond'), template_format='jinja2')
        # 构建chain
        chain = template | llm | StrOutputParser()

        # 调用LLM ---> 得到闲聊轨道的回复
        text = await chain.ainvoke({
            'user_message': user_message_str,
            'history': history
        })

        return [BotMessage(text=text)]


if __name__ == "__main__":
    t = '聊聊关于{{topic}}的话题吧'
    tem = PromptTemplate(template=t)
    print(tem.invoke({'topic':'自然语言处理'}))




        