import requests
from openai  import OpenAI
from atguigu.config.config import settings
import base64

url = settings.tts_base_url
client = OpenAI(
    api_key=settings.tts_api_key,
    base_url=settings.tts_base_url
)

def mimo_tts(text: str):

    user_content = '''
    角色：百年门阀岑家的现任大当家。自出生便被过继给祖庙的守门老人抚养，被塑造成一尊完美无瑕、绝情断欲的家族图腾。常年深居简出，对人有着极强的阶级疏离感。

    场景：在祠堂的阴影里，看着那个不顾一切冲破保安防线来找她、企图带她私奔的男人。她要用最冷硬的阶级壁垒，绞杀对方，也绞杀自己刚刚萌芽、却足以燎原的感情。

    指导：
    冰冷、慵懒却极具威压的低音御姐。发声通道非常松弛，没有任何剑拔弩张，却有着让人骨里生寒的压迫感。

    - 语速与顿挫：极慢，每个字都像是在舌尖滚过才吐出来，带着上位者漫不经心的傲慢。句与句之间留下极长的、令人不安的空白。
    - 气声与实声：大部分时间，她的声音没有明显的声调起伏，实音重且硬，像是一条平缓却冰冷的暗河。但一定要在某些尾音处（如“真心”），加入极其轻微的气音收束，透出一丝连她自己都没察觉到的疲惫与渴望。
    - 咬字肌理：文白杂糅的用词带着旧时代的痕迹，唇齿音发得极轻但极清晰（如“冲撞”“廉价”），显得既清雅又锋利，刀刀见血。
    '''
    user_content = '''
    角色: 顶级电商平台的资深客服主管，工号0001。从业十年，处理过上万起纠纷，练就了一套滴水不漏的“标准微笑话术”。她的温柔是精密的防御机制，耐心是冰冷的商业策略。

    场景：凌晨两点，值班时接到一位VIP客户的电话。对方因冲动消费后想退款未果，迁怒于她，用最恶毒的语言辱骂她“冷血的AI”。她轻轻摘下耳麦，对着屏幕露出标准八颗牙的微笑，然后用最专业温柔的声音，一字一句念出“很抱歉给您带来不便”。

    指导：
    温和、匀速却带着精密机械感的职业女声。发声位置靠前，始终保持“微笑共鸣腔”，却没有任何真实情绪波动。

    - 语速与顿挫：中等偏快，像运转流畅的流水线。每个字都经过标准培训的等距间隔，句尾上扬的职业化尾音精准得像测量过。但在一连串致歉后，会有一个极短的、几乎无法察觉的停顿——那是真实人格的裂缝。
    - 气声与实声：全程以柔和的实音为主，夹杂适度的气声以显得“真诚”。但在重复某些固定话术（如“我理解您的心情”）时，气声会突然消失，变成干燥的、逐字吐出的实音，透出程序般的冷酷。
    - 咬字肌理：大量使用行业标准话术（“请您知悉”“感谢您的耐心”），舌面音发得圆润饱满，听感舒适。但在说到“您有权投诉我”的“权”字时，会不自觉地加重唇齿的爆破感，像一把藏在天鹅绒里的手术刀。


    '''
    completion = client.chat.completions.create(
        model=settings.tts_model,
        messages=[
            {
                "role": "user",
                # "content": "Bright, bouncy, slightly sing-song tone — like you're bursting with good news you can barely hold in. Fast pace, rising pitch at the end."
                "content": user_content
            },
            {
                "role": "assistant",
                "content": text
            }
        ],
        audio={
            "format": "mp3",
            # "voice": settings.tts_voice,
            "optimize_text_preview": True
        }
    )

    message = completion.choices[0].message
    audio_bytes = base64.b64decode(message.audio.data)
    return audio_bytes



def tts(text: str):

    payload = {
        "model": settings.tts_model,
        "input": text,
        "voice": f"{settings.tts_model}:{settings.tts_voice}",
        "response_format": "mp3",
        "stream": True
    }

    headers = {
        "Authorization": f"Bearer {settings.tts_api_key}",  # 请替换为您的真实 API Key
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers, stream=False)
    if response.status_code == 200:
        print(type(response.content))
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
    return response.content  # type: <class 'bytes'>

# if response.status_code == 200:
#     print(type(response.content))

#     print("音频已成功保存为 output.mp3")
# else:
#     print(f"请求失败，状态码: {response.status_code}")
#     print(f"错误信息: {response.text}")

if __name__ == "__main__":
    print(type(tts('大家好')))
