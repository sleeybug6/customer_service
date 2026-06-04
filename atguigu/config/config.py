from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE_PATH = Path(__file__).parents[2] / '.env'

class Settings(BaseSettings):
    """
    1. 自动从指定的.env文件中读取该文件下的所有key以及值 并且自动存放到该类（实例）的属性中去
    2. 类型校验（自动的类型转换） os.getenv('APP_PORT')
    3.  SettingsConfigDict()实例之后一定要用变量接收一下 不然就被回收掉了而且变量名一定要叫默认使用的model_config
    """
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, env_file_encoding='utf-8', extra='ignore') 
    # 参数extra='ignore'表示.env文件中有的变量有但是当前配置没有定义的话不会导致报错

    llm_model: str
    llm_base_url: str
    llm_api_key: str
    commerce_api_base_url: str
    database_url: str
    app_host: str
    app_port: int

    # TTS
    tts_base_url: str
    tts_api_key: str
    tts_model: str
    tts_voice: str


settings = Settings() # type:ignore

if __name__ == "__main__":
    
    print(settings.llm_model)


    
    



