
from langchain_core.prompts import ChatPromptTemplate
x:list|None = None
# x:int|None = None

def init_x():
    global x
    # x = [1,2,3]
    x = 66



chat_template = ChatPromptTemplate([{'role':'system', 'content': '你是{角色}'}, {'role':'user', 'content':'你是谁?'}])
chat_template = ChatPromptTemplate([('system','你是{角色}'), ('human', '你是谁'), ('ai', '我是。。。')])

print(chat_template.invoke({'角色':'好人'}))




