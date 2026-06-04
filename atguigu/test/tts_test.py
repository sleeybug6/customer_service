import requests

url = "https://api.siliconflow.cn/v1/audio/speech"

payload = {
    "model": "fnlp/MOSS-TTSD-v0.5",
    "input": "你站在桥上看风景，看风景的人在楼上看你。明月装饰了你的窗子，你装饰了别人的梦",
    "voice": "fnlp/MOSS-TTSD-v0.5:bella",
    "response_format": "mp3",
    "stream": True
}

headers = {
    "Authorization": "Bearer sk-lyeeneobbsqaxunxkftkhithxfsegaddgxtapsyhilplofig",  # 请替换为您的真实 API Key
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers, stream=False)

if response.status_code == 200:
    
    with open('audio1.mp3', 'wb') as f:
        f.write(response.content)
    # 将流式响应写入文件
    # with open("output.mp3", "wb") as f:
    #     for chunk in response.iter_content(chunk_size=1024):
    #         if chunk:
    #             f.write(chunk)
    print("音频已成功保存为 audio1.mp3")
else:
    print(f"请求失败，状态码: {response.status_code}")
    print(f"错误信息: {response.text}")




curl -X POST 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
-H "Authorization: Bearer sk-ab05f11e753c4ffb8f1980648ca594a4" \
-H 'Content-Type: application/json' \
-d '{
    "model": "qwen3-tts-flash",
    "input": {
        "text": "那我来给大家推荐一款T恤，这款呢真的是超级好看，这个颜色呢很显气质，而且呢也是搭配的绝佳单品，大家可以闭眼入，真的是非常好看，对身材的包容性也很好，不管啥身材的宝宝呢，穿上去都是很好看的。推荐宝宝们下单哦。",
        "voice": "Cherry",
        "language_type": "Chinese"
    }
}'