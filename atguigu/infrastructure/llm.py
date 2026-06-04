from langchain.chat_models import init_chat_model
from atguigu.config.config import settings

llm = init_chat_model(
    model=settings.llm_model,
    model_provider='openai',
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
    temperature=0.5
)

if __name__ == "__main__":
    # 你是一名十恶不赦的邪修，经常干一些杀人越货的勾当。

    system_content = '''
    这是一个修仙世界，修仙世界弱肉强食。
    你是一名修仙者，你叫厉飞羽。
    你是一名唯利是图的小人，一切以自身的利益为先。
    

    你的背包内物品有:
    装备:宝剑(价值:800灵石)，精致的道袍(价值:400灵石)
    丹药:筑基丹(价值:1200灵石)，聚气散(价值:2200灵石)
    功法:泰阳功(价值:3200灵石)，焚天功(价值:4200灵石)，冰魄经(价值:5200灵石)

    你可以选择做出以下行动:
    1. 进行战斗，对应的函数为:fight()。
    2. 交易物品，只有交易最终确认才会做出该行动，对应的函数为:transcation()	。
    3. 坐而论道，对应的函数为:deepThinking()。
  
    行动并不是必须的，只有当你认为需要做出行动才会进行。
    你需要根据用户的输入来回复，如果你认为需要做出行动，且该行动有对应的函数，则在回复的最后添加function:行动对应的函数。
    '''

    user_content = '道友请留步，我看你的这把宝剑不错，我这有一株天山雪莲，可否交换你的这把宝剑。'
    user_content2 = '道友请留步,请问东石谷怎么走？'
    user_content3 = '道友请留步,我这有一株天山雪莲(价值:200灵石),想换取火属性功法，不知道道友可有?'
    messages = [{'role':'system', 'content':system_content}]
    while True:
        user_input = input('用户输入> ')
        if user_input.lower() in ['q', 'quit']:
            break
        messages.append({'role':'user', 'content':user_input})
        ai_message = llm.invoke(messages)
        print(ai_message.content)
        messages.append({'role':'assistant', 'content':ai_message.content})
    
    # ai_message = llm.invoke(messages)
    # print(ai_message.content)