
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from atguigu.domain.messages import UserMessage, BotMessage
from atguigu.domain.state import Turn
from atguigu.knowledge.providers import KnowledgeChunk
from atguigu.prompts.history_builder import HistoryBuilder
from atguigu.prompts.loader import load_prompt
from atguigu.infrastructure.llm import llm


class KnowledgeResponser:

    async def respond(self, user_message: UserMessage, recent_turns: list[Turn], chunks: list[KnowledgeChunk]) -> list[BotMessage]:
        """
        根据用户消息、历史对话以及知识提供商给的知识内容回复

        Args:
            user_message (UserMessage): 用户当前发来的消息
            recent_turns (list[Turn]): 历史对话
            chunks (list[KnowledgeChunk]): 提供商检索到的知识

        Returns:
            list[BotMessage]: _description_
        """

        # 准备提示词上下文
        user_message_str = HistoryBuilder._render_user_message(user_message)
        history = HistoryBuilder.build(recent_turns)
        knowledge_content = "\n\n".join([chunk.content for chunk in chunks])

        # 构造chain
        prompt_text = load_prompt("knowledge_respond")
        prompt = PromptTemplate.from_template(
            prompt_text,
            template_format="jinja2"
        )
        chain = prompt | llm | StrOutputParser()

        # 运行chain
        response = await chain.ainvoke({
            "user_message": user_message_str,
            "history": history,
            "knowledge_content": knowledge_content,
        })

        return [BotMessage(text=response)]