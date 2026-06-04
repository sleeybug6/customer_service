from atguigu.domain.messages import BotMessage
from atguigu.chitchat.responser import ChitchatResponser
from atguigu.domain.state import DialogueState



class ChitchatHandler:
    
    def __init__(self, responser: ChitchatResponser) -> None:
        self.responser = responser

    async def handle(self, states: DialogueState) -> list[BotMessage]:
        '''处理闲聊轨道'''


        user_message = states.pending_turn.user_message
        recent_turns = states.current_session().turns[-5:]
        

        return await self.responser.respond(user_message=user_message, recent_turns=recent_turns)



