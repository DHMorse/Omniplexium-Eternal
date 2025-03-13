import os
from huggingface_hub import InferenceClient

from secret_const import HUGGING_FACE_API_KEY

COLORS: dict[str, str] = {
    'red': '\u001b[1;31m',
    'yellow': '\u001b[1;33m',
    'blue': '\u001b[1;34m',
    'green': '\u001b[1;32m', # Don't use this color in discord
    'reset': '\u001b[0m'
}

SERVER_ID: int = 1304226624534745128



# Channel IDs
LOG_CHANNEL_ID: int = 1304829859549155328

ADMIN_LOG_CHANNEL_ID: int = 1304245019300986941

MODEL_ERROR_LOG_CHANNEL_ID: int = 1331289066192375858

WARNING_LOG_CHANNEL_ID: int = 1330672423288176700

CENSORSHIP_CHANNEL_ID: int = 1327794720407031829

LOGIN_REMINDERS_CHANNEL_ID: int = 1328894619303542877

CREDITS_CHANNEL_ID: int = 1329652683463852114

PRIVATE_CHANNEL_IDS: list[int] = [1304244993497501716, # admin-text
                                1304245019300986941, # admin-log
                                1331289066192375858, # model-error-log
                                1330672423288176700, # warning-log
                                1327794720407031829, # censor-log
                                1328204580454137986, # tests-output-log
                                1307923750666371082, # cardinal-system
                                1304245049319493643, # Admin VC
                                ]


# Role IDs
LOGIN_REMINDER_ROLE_ID: int = 1328548080555130911



# File paths list
FILE_PATHS: list[str] = []



# Paths
ROOT_DIR: str = os.path.expanduser('~/Documents/myCode/Omniplexium-Eternal')
FILE_PATHS.append(ROOT_DIR)

DATABASE_PATH: str = os.path.join(ROOT_DIR, 'discorddb.db')
FILE_PATHS.append(DATABASE_PATH)

IMG_PATH: str = os.path.join(ROOT_DIR, 'img')
FILE_PATHS.append(IMG_PATH)

CACHE_PATH: str = os.path.join(ROOT_DIR, 'cache')
FILE_PATHS.append(CACHE_PATH)

CARD_IMG_PATH: str = os.path.join(IMG_PATH, 'cards')
FILE_PATHS.append(CARD_IMG_PATH)

IMG_CARDS_STATIC_PATH: str = os.path.join(CARD_IMG_PATH, 'static')
FILE_PATHS.append(IMG_CARDS_STATIC_PATH)



# Pics
CACHE_DIR_PFP: str = os.path.join(CACHE_PATH, 'pfps')
FILE_PATHS.append(CACHE_DIR_PFP)

LEADERBOARD_PIC: str = os.path.join(CACHE_PATH, 'leaderboard.png')
FILE_PATHS.append(LEADERBOARD_PIC)

DEFUALT_PROFILE_PIC: str = os.path.join(IMG_PATH, 'defualt.png')
FILE_PATHS.append(DEFUALT_PROFILE_PIC)

CARD_TEMPLATE_PATH: str = os.path.join(IMG_CARDS_STATIC_PATH, 'cardTemplate.png')
FILE_PATHS.append(CARD_TEMPLATE_PATH)

CARD_IMG_PFP_PATH: str = os.path.join(CARD_IMG_PATH, 'pfp')
FILE_PATHS.append(CARD_IMG_PFP_PATH)

CARD_IMG_CARD_PATH: str = os.path.join(CARD_IMG_PATH, 'card')
FILE_PATHS.append(CARD_IMG_CARD_PATH)



# Hugging Face API
HUGGING_FACE_API_KEY_CLIENT: InferenceClient = InferenceClient(api_key=HUGGING_FACE_API_KEY)

MAIN_CENSORSHIP_MODEL: str = 'Qwen/Qwen2.5-72B-Instruct'

BACKUP_CENSORSHIP_MODEL: str = 'meta-llama/Llama-3.2-3B-Instruct'