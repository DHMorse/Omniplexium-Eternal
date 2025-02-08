import os
from helperFunctions.main import logWarning
from const import CACHE_PATH, FILE_PATHS, COLORS


async def verifyFilePaths(bot):
    for filePath in FILE_PATHS:
        if not CACHE_PATH in filePath:
            if not os.path.exists(filePath) and not filePath.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.db')):
                os.makedirs(filePath)
                print(f"{COLORS['yellow']}Created {filePath}{COLORS['reset']}")
                await logWarning(bot, f"File path {filePath} did not exist, so it was created.")
            else:
                if not os.path.exists(filePath):
                    print(f"{COLORS['yellow']}Warning: {filePath} does not exist{COLORS['reset']}")
                    await logWarning(bot, f"{filePath} does not exist")
    
    print(f"{COLORS['blue']}Verified all file paths{COLORS['reset']}")