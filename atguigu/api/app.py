from contextlib import asynccontextmanager
from fastapi import  FastAPI

from atguigu.api.dependencies import init_dialogue_engine
from atguigu.api.router.chat_router import chat_router
from atguigu.infrastructure.database import init_db_engine, close_db_engine
from atguigu.infrastructure.http import init_http_client, close_http_client

@asynccontextmanager
async def lifespan(app:FastAPI):
    """
    1. 回调lifespan的时机: 在FastAPI服务启动时先调用
    2. 参数app以及类型需要指定: 因为FastAPI底层会对资源做共享和传递
    3  在FastAPI服务关闭前会再次调用lifespan
    """

    # FastAPI服务启动时先执行 (如初始化HTTP客户端、数据库连接池、Redis客户端...)
    init_db_engine()
    init_dialogue_engine()
    init_http_client()

    yield

    # FastAPI服务关闭前先执行
    await close_db_engine()
    await close_http_client()




app = FastAPI(description='电商小二智能客服应用', lifespan=lifespan)


app.include_router(chat_router)