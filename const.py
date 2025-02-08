import os
from huggingface_hub import InferenceClient
from typing import List

from secret_const import HUGGING_FACE_API_KEY

COLORS = {
    'red': '\u001b[1;31m',
    'yellow': '\u001b[1;33m',
    'blue': '\u001b[1;34m',
    'green': '\u001b[1;32m', # Don't use this color in discord
    'reset': '\u001b[0m'
}

SERVER_ID = 1304226624534745128



# Channel IDs
LOG_CHANNEL_ID = 1304829859549155328

ADMIN_LOG_CHANNEL_ID = 1304245019300986941

MODEL_ERROR_LOG_CHANNEL_ID = 1331289066192375858

WARNING_LOG_CHANNEL_ID = 1330672423288176700

CENSORSHIP_CHANNEL_ID = 1327794720407031829

LOGIN_REMINDERS_CHANNEL_ID = 1328894619303542877

CREDITS_CHANNEL_ID = 1329652683463852114

PRIVATE_CHANNEL_IDS: List[int] = [1304244993497501716, # admin-text
                                1304245019300986941, # admin-log
                                1331289066192375858, # model-error-log
                                1330672423288176700, # warning-log
                                1327794720407031829, # censor-log
                                1328204580454137986, # tests-output-log
                                1307923750666371082, # cardinal-system
                                1304245049319493643, # Admin VC
                                ]


# Role IDs
LOGIN_REMINDER_ROLE_ID = 1328548080555130911



# Paths
ROOT_DIR = os.path.expanduser('~/Omniplexium-Eternal')

DATABASE_PATH = os.path.join(ROOT_DIR, 'discorddb.db')

CURRENT_ITEM_ID_PATH = os.path.join(ROOT_DIR, 'currentItemID.txt')

IMG_PATH = os.path.join(ROOT_DIR, 'img')

# Pics

CACHE_DIR_PFP = os.path.join(ROOT_DIR, 'cache', 'pfps')

LEADERBOARD_PIC = os.path.join(ROOT_DIR, 'leaderboard.png')

DEFUALT_PROFILE_PIC = os.path.join(IMG_PATH, 'defualt.png')

CARD_TEMPLATE_PATH = os.path.join(IMG_PATH, 'cardTemplate.png')


# Hugging Face API
HUGGING_FACE_API_KEY_CLIENT = InferenceClient(api_key=HUGGING_FACE_API_KEY)

MAIN_CENSORSHIP_MODEL = 'Qwen/Qwen2.5-72B-Instruct'

BACKUP_CENSORSHIP_MODEL = 'meta-llama/Llama-3.2-3B-Instruct'