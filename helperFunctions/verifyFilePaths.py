import os
from helperFunctions.main import logWarning
from const import FILE_PATHS, COLORS


async def verifyFilePaths(bot):
    for filePath in FILE_PATHS:
        if not os.path.exists(filePath):
            os.makedirs(filePath)
            print(f"{COLORS['yellow']}Created {filePath}{COLORS['reset']}")
            logWarning(bot, f"File path {filePath} did not exist, so it was created.")
        else:
            print(f"{COLORS['blue']}Verified {filePath}{COLORS['reset']}")