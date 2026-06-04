import uuid
from fastapi import APIRouter, Depends, Response
from atguigu.api.dependencies import get_dialogue_service
from atguigu.api.schemas import ChatBotMessage, ChatMessageResponse, ChatObject, ChatRequest, ChatResponse, TTSRequest, ChatHistory
from atguigu.domain.messages import FocusedObject, UserMessage, MessageType, ProcessResult
from atguigu.service.dialogue_service import DialogueService

from atguigu.infrastructure.tts import mimo_tts

chat_router = APIRouter()




@chat_router.post('/api/chat')
async def chat_endpoint(chat_request: ChatRequest, dialogue_service:DialogueService=Depends(get_dialogue_service)) -> ChatResponse:

    # 1. 将接过来的ChatRequest类型的数据转成业务逻辑需要的数据类型
    user_message: UserMessage = _build_user_message(chat_request)

    # 2. 业务处理  `ProcessResult` 是引擎处理一轮对话的结果
    process_result: ProcessResult = await dialogue_service.handle_message(user_message)


    # 3. 将业务处理结果转成ChatResponse返回  
    return _build_chat_response(process_result)

@chat_router.get('/api/chat/history')
async def history_endpoint(sender_id: str, service: DialogueService=Depends(get_dialogue_service)) -> ChatMessageResponse:


    
    chat_response: ChatMessageResponse = await service.load_chat_history(sender_id)

    return chat_response





@chat_router.post('/api/chat/tts')
async def tts_endpoint(text:TTSRequest):
    
    return Response(content=mimo_tts(text.text), media_type="audio/mpeg")



    

def _build_user_message(chat_request: ChatRequest) -> UserMessage:
    '''将请求数据模型(ChatRequest)转成业务逻辑需要的领域模型(UserMessage)'''

    return UserMessage(
        sender_id=chat_request.sender_id,
        message_id=chat_request.message_id if chat_request.message_id else str(uuid.uuid4()), # 如果前端发来的请求没有消息ID 则uuid生成
        type=MessageType.TEXT if chat_request.text else MessageType.OBJECT,
        text=chat_request.text,
        object=FocusedObject(
            id=chat_request.object.id,
            type=chat_request.object.type,
            title=chat_request.object.title,
            attributes=chat_request.object.attributes

        ) if chat_request.object else None

    )

def _build_chat_response(process_result: ProcessResult) -> ChatResponse:
    '''将业务处理结果ProcessResult类型 ---> 转成给前端响应需要的类型ChatResponse'''
    
    return ChatResponse(
        sender_id=process_result.sender_id,
        message_id=process_result.message_id,
        messages=[ChatBotMessage(
            text=bot_message.text,
            object=ChatObject(
                id=bot_message.object.id,
                type=bot_message.object.type,
                title=bot_message.object.title,
                attributes=bot_message.object.attributes
            ) if bot_message.object else None 
        )
        for bot_message in process_result.bot_messages]
    )






