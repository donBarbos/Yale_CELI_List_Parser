from typing import Callable
from dotenv import load_dotenv

import os
import random
import time

load_dotenv()
CELI_SITE_URL: str  = (
    os.getenv('CELI_SITE_URL')
    or "https://som.yale.edu/story/2022/over-1000-companies-have-curtailed-operations-russia-some-remain"
)
BROWSER_DIR: str = os.getenv('BROWSER_DIR') or "my_browser"
PATH_TO_DUMP: str = (
    os.getenv('PATH_TO_DUMP')
    or "Yale_CELI_List_of_Companies_Leaving_and_Staying_in_Russia.csv"
)

# for more realism: sleep(1) = time.sleep(1+-0.2), with slippage 0.2s
sleep: Callable[[float], None] = lambda s: time.sleep(random.uniform(s - 0.2, s + 0.2))
