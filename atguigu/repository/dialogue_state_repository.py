import json
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from atguigu.domain.state import DialogueState
from atguigu.model.dialogue_state_record import DialogueStateRecord

class DialogueStateRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def load(self, sender_id: str) -> DialogueState:
        '''
        读操作:
        根据用户id从数据库中查询该用户的数据
        '''

        # 从数据库中根据sender_id查询数据
        stmt = select(DialogueStateRecord).where(DialogueStateRecord.sender_id==sender_id)
        dialogue_state: DialogueStateRecord | None = await self.session.scalar(stmt)

        # 判断是否存在
        if dialogue_state:
            state_dic = json.loads(dialogue_state.state_json)
            return DialogueState.from_dict(state_dic)
        
        # 如果该用户id不存在 --- 则创建新的
        return DialogueState(sender_id=sender_id)
        

    async def save(self, dialogue_state: DialogueState):
        '''
        写操作
        将DialogueState对象 ---> 转成dict ---> 再通过json.dumps转成字符串 ---> 存入数据库
        '''

        # 转换成字符串
        state_json: str = json.dumps(dialogue_state.to_dict(), ensure_ascii=False)

        # 定义插入sql语句     
        insert_stmt  = insert(DialogueStateRecord).values(sender_id=dialogue_state.sender_id, state_json=state_json)
        
        # 如果插入数据的主键已经存在 ---> 则进行更新 相当将原本的inser_stmt改造成了upsert
        update_stmt = insert_stmt.on_duplicate_key_update(state_json=insert_stmt.inserted.state_json)

        # 执行
        await self.session.execute(update_stmt)
        
        await self.session.commit()


        


