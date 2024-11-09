import os
import math

ROOT_DIR = os.path.expanduser('~/Documents/Omniplexium-Eternal/')

CACHE_DIR_PFP = os.path.join(ROOT_DIR, 'cache_dir', 'pfps')

LEADERBOARD_PIC = os.path.join(ROOT_DIR, 'leaderboard.png')

DEFUALT_PROFILE_PIC = os.path.join(CACHE_DIR_PFP, 'defualt.png')

def xpToLevel(experience: int, base: int = 10) -> int:
    return int(math.log(experience + 1, base)) + 1
