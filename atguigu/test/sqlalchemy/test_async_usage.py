"""
sqlalchemy的异步用法
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, insert
from models import Base, User, Address

async def async_main():
    # 创建异步引擎
    engine = create_async_engine(url='mysql+aiomysql://root:123456@127.0.0.1:3306/async_test?charset=utf8mb4', echo=False)

    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    

    # 添加数据
    user1 = User(name='zs5')
    user2 = User(name='ls5')
    user3 = User(name='ww5')

    # 创建异步session工厂  expire_on_commit:提交之后 变量是否就过期, 默认过期，要保留需设置为False:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)


    # 使用工厂创建session对象
    async with session_factory() as session:
    # async with AsyncSession(engine) as session:
        # session.add_all([user1, user2, user3])

        
        results = (await session.execute(select(User))).scalars()
        # results = await session.scalars((select(User))) # 与上面等价

        print(type(results)) # ScalarResult类型
        for u in results:
            print(u)  # u为 User类型

        user = await session.scalar(select(User).where(User.name=='zs6'))
        
        
        print(user)

        # await session.execute(insert(User).values(name='ww'))
        await  session.commit()
    
    print(user) # 如果设置expire_on_commit=True, 这里的user就是用不了了

    
    
    await engine.dispose()


    

if __name__ == "__main__":
    asyncio.run(async_main())