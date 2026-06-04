"""
未来使用http请求的方式调用中台接口查询订单数据、商品数据...
"""

import asyncio
from httpx import AsyncClient

http_client:AsyncClient 

def init_http_client():
    global http_client
    http_client = AsyncClient(timeout=10)

async def close_http_client():
    await http_client.aclose() # type:ignore

async def main():
    # 初始化http客户端
    init_http_client()

    response = await http_client.get(url='http://192.168.10.128:18081/users/u1001/orders')
    
    print(type(response.json())) # <class 'dict'>
    # print(response.json()['data']['orders'])
if __name__ == "__main__":

    asyncio.run(main())
    



