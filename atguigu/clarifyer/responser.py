import json

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.plan.turn_plan import ClarifyReason, TurnPlanValidationResult
from atguigu.prompts.history_builder import HistoryBuilder
from atguigu.prompts.loader import load_prompt
from atguigu.infrastructure.llm import llm



class ClarifyResponser:
    def __init__(self) -> None:
        pass

    async def respond(self, states: DialogueState, reason: ClarifyReason) -> list[BotMessage]:
        clarify_message = self._build_clarify_message(states, reason)
        user_message = states.pending_turn.user_message
        user_message_str = HistoryBuilder._render_user_message(user_message)
        history_str = HistoryBuilder.build(states.current_session().turns[-10:])
        focused_object_str = json.dumps(states.focused_object.to_dict(), ensure_ascii=False) if states.focused_object else None

        # 构建提示词
        template = load_prompt('clarify_respond')
        prompt_template = PromptTemplate.from_template(template=template, template_format='jinja2')
        # 构建chain
        chian = prompt_template | llm | StrOutputParser()

        # 调用LLM 重写机器人回复
        rewritten = await chian.ainvoke({
            'user_message': user_message_str,
            'history': history_str,
            'focused_object': focused_object_str,
            'clarify_message': clarify_message,
            'reason': reason.value
        })

        return [BotMessage(text=rewritten)]





    def _build_clarify_message(self, states: DialogueState, reason: ClarifyReason) -> str:

        if reason is ClarifyReason.MULTIPLE_TRACKS:
            return "你这次同时提到了多个方向。我们先处理一个，你想先办业务还是先咨询信息呢？"

        if reason is ClarifyReason.MISSING_FOCUSED_OBJECT:
            return "请先发送你想咨询的对象，我再继续帮你看。"

        if reason is ClarifyReason.MISSING_KNOWLEDGE_INTENT:
            return "你是想了解商品信息、订单信息，还是售后配送规则呢？"

        if reason is ClarifyReason.MISSING_TRACK:
            return "你是想先处理业务问题，还是先咨询信息呢？"

        if reason is ClarifyReason.MISSING_TASK_COMMANDS:
            return "你这次是想办理什么业务呢？比如查订单、查物流，或者申请退款。"

        if reason is ClarifyReason.OBJECT_REQUIRES_INTENT:
            focused_object = states.focused_object
            if focused_object is not None and focused_object.type == "order":
                return "我已经收到这个订单了。你想查订单状态、查物流，还是申请退款呢？"
            if focused_object is not None and focused_object.type == "product":
                return "我已经收到这个商品了。你想了解它的商品信息、发货情况，还是售后相关问题呢？"

        return "我还需要再确认一下你的意思，你可以换个更具体的说法告诉我。"
