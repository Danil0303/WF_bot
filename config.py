import os

from dotenv import load_dotenv
from dataclasses import dataclass
load_dotenv('.env')

@dataclass
class SettingConfig:
    token: str = os.getenv("TOKEN")
    channel_id:str = os.getenv('ID_CHANNEL')
    dp_path: str = os.getenv("DB_PATH")

@dataclass
class YooKasConfig:
    api_key: str = os.getenv('API_KEY')
    shop_id: int =os.getenv('SHOP_ID')
    link: str = os.getenv("LINKS")
    return_url_api: str = os.getenv('RETURN_URL')
    value_cur: float = os.getenv("VALUE_CUR")
    time_delta: int = os.getenv("TIME_DELTA", 10)