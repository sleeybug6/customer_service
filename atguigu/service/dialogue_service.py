


from atguigu.api.schemas import ChatHistory, ChatMessageResponse
from atguigu.domain.messages import ProcessResult, UserMessage
from atguigu.domain.state import DialogueState, Session
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.prompts.history_builder import HistoryBuilder
from atguigu.repository.dialogue_state_repository import DialogueStateRepository


class DialogueService:
    '''处理对话的业务类'''

    def __init__(self, dialogue_state_repository:DialogueStateRepository, dialogue_engine: DialogueEngine):
        self.dialogue_state_repository = dialogue_state_repository
        self.dialogue_engine = dialogue_engine

    async def handle_message(self, user_message:UserMessage) -> ProcessResult:
        '''
        处理用户消息 返回处理结果
        大致流程: 从数据库中取该用户的数据 -> 业务处理 -> 再往数据库中存处理后的数据
        '''

        # 1. 从数据库中load对话状态聚合根  --- O阶段  存取操作 ---> 使用repository对象
        dialogue_state: DialogueState = await self.dialogue_state_repository.load(user_message.sender_id)
   
        # 2. 调用引擎 使用对话状态对象进行业务的各种计算操作  引擎内部会根据业务逻辑原地修改对话状态dialogue_state
        process_result: ProcessResult = await self.dialogue_engine.handle_dialogue(dialogue_state, user_message)


        # 3. 通过save 将对话状态dialogue_state(已被引擎修改过的)聚合根  写入到数据库中 --- I阶段
        await self.dialogue_state_repository.save(dialogue_state)



        return process_result
    

    async def load_chat_history(self, sender_id: str) -> ChatMessageResponse: 

        # 获取用户的所有对话状态
        states: DialogueState = await self.dialogue_state_repository.load(sender_id=sender_id)


        chat_messages: list[ChatHistory] = []
        # 遍历所有session
        for session in states.sessions:

            for turn in session.turns:
                chat_messages.append(HistoryBuilder._render_chat_history_user_message(turn.user_message, session))
                bot_messages = [HistoryBuilder._render_chat_history_bot_message(bot_msg, session) for bot_msg in turn.bot_messages]
                chat_messages.extend(bot_messages)
        
        return ChatMessageResponse(
            sender_id=sender_id,
            messages=chat_messages

        )
    



                
