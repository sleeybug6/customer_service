from atguigu.knowledge.providers import KnowledgeProvider


class KnowledgeProviderRegistry:
    '''知识库提供商注册类'''

    def __init__(self, providers: list[KnowledgeProvider]) -> None:
        
        self._providers_by_id:dict[str, KnowledgeProvider] = {p.provider_id: p for p in providers}
    
    def get(self, provider_id: str) -> KnowledgeProvider:
        '''根据提供商id获取提供商对象'''

        return self._providers_by_id[provider_id]
