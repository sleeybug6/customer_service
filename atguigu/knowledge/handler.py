

from atguigu.domain.messages import BotMessage
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.domain.state import DialogueState
from atguigu.knowledge.responser import KnowledgeResponser
from atguigu.knowledge.providers import KnowledgeProvider, KnowledgeChunk
from atguigu.knowledge.registry import KnowledgeProviderRegistry

class KnowledgeHandler:
    def __init__(self, knowledge_intents: dict[str, KnowledgeIntent], provider_registry: KnowledgeProviderRegistry, responser: KnowledgeResponser):
        self.knowledge_intents = knowledge_intents # 系统支持的所有支持意图注册表
        self.provider_registry = provider_registry # 知识提供商注册对象
        self.responser = responser  

    async def handle(self, states: DialogueState, intents: list[str]) -> list[BotMessage]:
        """
        处理知识咨询轨道
        Args:
            states (DialogueState): _description_
            intents (list[str]): LLMd得到的turn_plan中knowledge轨道的知识意图列表

        Returns:
            list[BotMessage]: _description_
        """        
 

        # 根据意图寻找知识来源
        provider_ids = self._get_provider_id_by_intents(intents)

        # 从每一个provider 检索知识片段
        chunks: list[KnowledgeChunk] = []
        for provider_id in provider_ids:
            # 根据提供商id获取提供商对象
            provider: KnowledgeProvider = self.provider_registry.get(provider_id)
            # 使用提供商提供的检索方法获取知识信息
            chunk = await provider.retrieve(states)
            chunks.extend(chunk)
        
        # 将检索到的知识作为LLM上下文生成回复
        return await self.responser.respond(user_message=states.pending_turn.user_message, recent_turns=states.current_session().turns[-5:], chunks=chunks)
        
    

    # 请问这件商品的退款以及退货政策是什么-----> intents=["return_policy","refund_policy"]
    def _get_provider_id_by_intents(self, intents: list[str]) -> list[str]:
        '''根据意图列表得到所有提供商的id'''

        provider_ids: list[str] = []
        for intent in intents:
            provider_ids.extend(self.knowledge_intents[intent].provider_ids)
        
        return list(set(provider_ids))
        