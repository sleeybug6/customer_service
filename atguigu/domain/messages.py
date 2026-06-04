"""

消息类型：两种
UserMessage(用户)
BotMessage(机器人)

to_dict:将实例对象转成字典对象
from_dict:将字典对象转成实例对象

"""

from typing import Dict, Any, Literal
from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel

# 定义用户发送消息的类型，是文本消息还是对象类型消息
class MessageType(Enum):
    TEXT = 'text'
    OBJECT = 'object'


@dataclass(slots=True)  # 设置slots=True访问速度更快(底层为数组而非dict)、内存占用更小。且无法动态添加额外的属性
class FocusedObject:
    id:str
    type:str
    title:str=''
    attributes:Dict[str, Any]=field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id':self.id,
            'type':self.type,
            'title':self.title,
            'attributes':dict(self.attributes)
        }

    @classmethod
    def from_dict(cls, data:Dict[str,Any]) -> "FocusedObject":
        return cls(
            id=data['id'],
            type=data['type'],
            title=data.get('title',''),
            attributes=data.get('attributes', {})
        )




@dataclass(slots=True)
class UserMessage:
    sender_id:str # 用户ID(必填字段)
    message_id:str # 消息ID(必填字段)
    type:MessageType # 用户发送的消息类型(必填字段)
    text:str | None = None # 文本类型消息内容
    object:FocusedObject | None = None # 对象类型消息

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sender_id':self.sender_id,
            'message_id':self.message_id,
            'type':self.type.value,
            'text':self.text,
            'object':self.object.to_dict() if self.object else None
        }

    @classmethod
    def from_dict(cls, data:Dict[str, Any]) -> "UserMessage": # data{'sender_id':'123', 'object':{'id':'123',...}...}
 
        return cls(
            sender_id=data['sender_id'],
            message_id=data['message_id'],
            type=MessageType(data['type']),
            text=data.get('text'),
            object=FocusedObject.from_dict(data['object']) if data.get('object') else None
        )

@dataclass(slots=True)
class BotMessage:
    text:str | None = None
    object:FocusedObject | None = None 

    def to_dict(self) -> Dict[str, Any]:
        return {
            'text':self.text,
            'object':self.object.to_dict() if self.object else None
        }
    
    @classmethod
    def from_dict(cls, data:Dict[str, Any]) -> 'BotMessage':
        return cls(
            text=data.get('text'),
            object=FocusedObject.from_dict(data['object']) if data['object'] else None
        )

@dataclass
class ProcessResult:
    sender_id: str # 用户ID
    message_id: str # 消息ID(需要内部生成)
    bot_messages: list[BotMessage]  # 这一轮(Turn)的回复消息

@dataclass(slots=True)
class ChatHistory:
    session_id: str
    role: Literal['user', 'bot']
    text: str | None = None
    object: FocusedObject | None = None

if __name__ == "__main__":
    # print(MessageType('object').value)
    import random
    
    with open('flow_config/user_flows.yml', 'r', encoding='utf-8') as f:
        pass


