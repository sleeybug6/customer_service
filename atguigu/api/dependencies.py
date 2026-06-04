
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.repository.dialogue_state_repository import DialogueStateRepository
from atguigu.service.dialogue_service import DialogueService
from atguigu.infrastructure import database
from atguigu.engine.builder import build_dialogue_engine

_dialogue_engine: DialogueEngine | None = None

async def get_session():
    '''获取数据库会话对象'''
    # async with database.session_factory() as session:
    async with database.session_factory() as session:
        yield session




async def get_dialogue_state_repository(session:AsyncSession=Depends(get_session)) -> DialogueStateRepository:
    '''获取对话的repository对象'''
    return DialogueStateRepository(session)

def init_dialogue_engine():
    # 构建引擎的方法
    global _dialogue_engine
    _dialogue_engine = build_dialogue_engine()
    pass

async def get_engine():
    '''获取对话引擎对象'''
    return _dialogue_engine


async def get_dialogue_service(
        dialogue_state_repository: DialogueStateRepository=Depends(get_dialogue_state_repository),
        dialogue_engine: DialogueEngine=Depends(get_engine),
    ) -> DialogueService:
    
    '''获取对话服务对象'''

    return DialogueService(
        dialogue_state_repository=dialogue_state_repository,
        dialogue_engine=dialogue_engine
    )


