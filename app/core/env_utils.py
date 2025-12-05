from dotenv import load_dotenv
import os

load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_BASE_URL = os.getenv('GOOGLE_BASE_URL')

ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
ZHIPU_BASE_URL = os.getenv('ZHIPU_BASE_URL')

QIANWEN_API_KEY = os.getenv('QIANWEN_API_KEY')
QIANWEN_BASE_URL = os.getenv('QIANWEN_BASE_URL')

WEB_SEARCH_URL=os.getenv('WEB_SEARCH_URL')

