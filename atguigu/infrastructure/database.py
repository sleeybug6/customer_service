"""
操作自己的数据库（customer_service） dialogue_states表（整个对话状态：聚合根）
使用session对象来操作数据库(CRUD)
"""

import asyncio
from sqlalchemy import select,text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from atguigu.config.config import settings


engine: AsyncEngine | None = None
session_factory:async_sessionmaker[AsyncSession] | None = None


def init_db_engine():
    global engine, session_factory
    # 创建引擎
    engine = create_async_engine(url=settings.database_url, echo=False)

    # 创建会话工厂
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

async def close_db_engine():
    await engine.dispose()

async def main():
    
    init_db_engine()
    async with session_factory() as session:
        sql = 'select 1' # 测试sql
        result = await session.execute(text(sql))
        print(result.fetchall())

    await close_db_engine()
if __name__ == "__main__":

    asyncio.run(main())
    

    




