import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    LUNARCRUSH_API_KEY=os.getenv('LUNARCRUSH_API_KEY')
    LUNARCRUSH_BASE_URL=os.getenv('LUNARCRUSH_BASE_URL')
    CG_API_KEY=os.getenv('CG_API_KEY')

