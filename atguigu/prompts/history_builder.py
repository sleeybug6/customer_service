
from atguigu.domain.messages import BotMessage, ChatHistory, FocusedObject, MessageType, UserMessage
from atguigu.domain.state import Session, Turn


class HistoryBuilder:
    '''
    1. 将用户信息UserMessage对象序列化为字符串
    2. 将历史对话的Q(UserMessage)和A(BotMessage)序列化为字符串, 并附加角色信息(是用户说的还是机器人说的)
    
    '''

    @staticmethod
    def build(turns: list[Turn]) -> str:
        """
        构建历史对话

        Args:
            turns (list[Turn]): _description_

        Returns:
            str: _description_
        """
        msg:list[str] = []
        for turn in turns:

            # 1. 用户消息
            user_message = turn.user_message
            user_message_str = HistoryBuilder._render_user_message(user_message)
            msg.append(f'USER: {user_message_str}')

            # 2. 机器人消息
            for bot_msg in turn.bot_messages:
                bot_msg_str = HistoryBuilder._render_bot_message(bot_msg)
                msg.append(f'BOT: {bot_msg_str}')
        
        return '\n'.join(msg)


        
    @staticmethod
    def _render_user_message(user_message: UserMessage) -> str:
        '''渲染用户消息'''

        if user_message.type == MessageType.TEXT:
            
            # 文本类型消息
            return HistoryBuilder._render_text_msg(user_message.text)
        else:
            # 对象类型消息
            return HistoryBuilder._render_object_msg(user_message.object)
        

    
    @staticmethod
    def _render_text_msg(text: str) -> str:
        '''返回去掉空格的干净字符串'''
        return text.strip()


    @staticmethod
    def _render_object_msg(obj: FocusedObject) -> str:
        """
        渲染对象消息
        Args:
            obj (FocusedObject): _description_

        Returns:
            str: 返回的内容例子如下：
            [id=1001, type=订单对象 or 商品对象, title=对应的描述, attributes='price=100 url=www.abc.com']
        """

        label = '订单对象' if obj.type == 'order' else '商品对象'
        id = obj.id
        title = obj.title
        attributes: dict = obj.attributes

        attributes_str = ' '.join([f'{k}={v}' for k,v in attributes.items()])

        return f'[label={label}, id={id}, title={title}, attributes={attributes_str}]'

    @staticmethod
    def _render_bot_message(bot_message: BotMessage) -> str:
        """渲染机器人消"""

        if bot_message.text:
            return bot_message.text
        else:
            # TODO
            bot_message.object


    @staticmethod
    def _render_chat_history_user_message(user_message: UserMessage, session: Session) -> ChatHistory:

        return ChatHistory(
            session_id=session.session_id,
            role='user',
            text=user_message.text,
            object=user_message.object
        )

    @staticmethod
    def _render_chat_history_bot_message(bot_message: BotMessage, session: Session) -> ChatHistory:

        return ChatHistory(
            session_id=session.session_id,
            role='bot',
            text=bot_message.text,
            object=bot_message.object
        )


