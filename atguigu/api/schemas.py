"""
定义接口的数据模型
请求相关:
响应相关:

ps: 
整个消息链路: 用户发来的消息会被schema的ChatRequest包装 ---> 转成domain中的模型给业务层逻辑使用 ---> 业务层处理完得到domain的ProcessResult类型
---> 再转成schema的ChatResponse类型发给前端 ---> 前端渲染给用户看
"""

from typing import Literal
from pydantic import BaseModel

from atguigu.domain.messages import ChatHistory


class ChatObject(BaseModel):
    
    id: str
    type: str
    title: str  = ''
    attributes: dict = {}



class ChatBotMessage(BaseModel):
    text: str | None = None
    object: ChatObject | None




class ChatRequest(BaseModel):
    '''用户发来的消息'''
    sender_id: str # 用户ID
    message_id: str | None = None  # 消息ID， 前端没给就为None，需要后端生成
    text: str | None = None  # 文本类型的消息
    object: ChatObject | None = None  # 对象类型的消息


class ChatResponse(BaseModel):
    sender_id: str
    message_id: str  # 要回复哪条消息
    messages: list[ChatBotMessage]  # Bot回复的内容


class TTSRequest(BaseModel):
    text: str



class ChatMessageResponse(BaseModel):
    sender_id: str
    messages: list[ChatHistory]
