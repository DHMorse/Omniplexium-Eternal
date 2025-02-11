# Omniplexium-Eternal: Admin Commands Guide

![Python](https://img.shields.io/badge/Python-3.10.12-blue?style=flat&logo=python&logoColor=white)
![SQLite3](https://img.shields.io/badge/SQLite-3.31.1-003B57?style=flat&logo=sqlite&logoColor=white)
![Discord](https://img.shields.io/badge/Discord-Blue?style=flat&logo=discord&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-5.0.17-4EAA25?style=flat&logo=gnu-bash&logoColor=white)


Welcome to the admin commands guide for Omniplexium-Eternal! Below you'll find detailed instructions on using commands to manage user stats, including resetting, setting values, and viewing stats. Required arguments are marked with an asterisk (*).

---

### Commands Overview
- **`!copycard`** - Copy a card and give it to a new player
- **`!leveltoxp`** - Displays the amount of xp required for a level
- **`!makeloginrewards`** - Generates the loginRewards table
- **`!reset`** - Reset a user’s stat
- **`!set`** - Set a specific stat to a given value
- **`!stats`** - Display a user’s stats
- **`!vanity`** - Display bot statistics
- **`!viewcard`** - View details of a specific card

---

### Command Details

## CopyCard Command

### Description
Copies a specific card to a user's collection. Allows copying by card ID or card name.

### Syntax
`!copycard {cardIdOrName}* {discord.Member}`

### Arguments
- **{cardIdOrName}** *(required)*: Identifier for the card
 - Accepts:
   - Card ID (numeric)
   - Full card name (multiple words supported)

- **{discord.Member}** *(optional)*: The Discord user to receive the card
 - Default: If no member is specified, copies the card to the command user

### Permissions
- Requires administrator privileges

### Usage Examples
`!copycard 123`           # Copies card with ID 123 to your own collection
`!copycard Rare Card`   # Copies card by name to your own collection
`!copycard 456 @User`     # Copies card with ID 456 to specified user's collection

### Behavior
- Converts multi-word card names into a single string
- Looks up card ID if a name is provided instead of a numeric ID
- Searches cards database to validate card name/ID
- Handles potential errors during card copying process

### Potential Errors
- Insufficient permissions
- Card not found
- Database connection issues
- Invalid card identifier

## LevelToXP Command

### Description
Converts a game level to the total XP (experience points) required to reach that level.

### Syntax
`!leveltoxp {level}`

### Arguments
- **{level}** *(required)*: The target game level
 - Must be an integer
 - Valid range: 1-100

### Permissions
- Requires administrator privileges

### XP Calculation Details
- Levels 1-10: Linear XP growth (10 XP per level)
- Levels 11-99: Exponential XP growth
- Level 100: Caps at maximum XP (10 trillion)

### Usage Examples
`!leveltoxp 1`     # Shows XP required to reach level 1
`!leveltoxp 50`    # Shows XP required to reach level 50
`!leveltoxp 100`   # Shows XP required to reach maximum level

### Potential Errors
- Invalid level input (non-integer)
- Level below 1
- Level above 100
- Insufficient permissions

### Notes
- XP calculation uses an exponential growth model
- Provides precise XP requirements for character progression

## MakeLoginRewards Command

### Description
Automatically generates a structured login reward system for game progression, creating a database table with rewards for each level.

### Syntax
`!makeloginrewards {numberOfLevels}`

### Arguments
- **{numberOfLevels}** *(required)*: Total number of levels to generate rewards for
 - Defines the extent of the login reward progression
 - Determines how many levels will have unique rewards

### Reward Generation Rules
- **Level 1**: Base XP reward
- **Every Level**: Incrementing XP rewards
- **Level 10**: Special card reward (Card ID: 6)
- **Every 5th Level**: Money reward
 - Money amount scales with level

### Reward Types
- `xp`: Experience points
 - Increasing amount with each level
 - XP increment grows progressively
- `money`: Currency reward
 - Amount calculated as `level * 2`
- `card`: Specific card reward
 - Currently hardcoded card at level 10

### Database Impact
- Creates `loginRewards` table if not existing
- Stores reward details:
 - `level`: Progression level
 - `rewardType`: Type of reward
 - `amountOrCardId`: Specific reward value

### Permissions
- Requires administrator privileges

### Usage Examples
`!makeloginrewards 50`   # Generates login rewards for first 50 levels
`!makeloginrewards 100`  # Generates login rewards for first 100 levels

### Potential Errors
- Insufficient permissions
- Database connection issues
- Invalid number of levels

## Reset Command

### Description
Allows administrators to reset specific user statistics to their default values, with a confirmation step to prevent accidental resets.

### Syntax
`!reset {stat}* {discord.Member}`

### Arguments
- **{stat}** *(required)*: The statistic to reset
 - Supported options:
   - `xp`: Resets user's experience points
   - `money`: Resets user's currency balance
   - `lastLogin`: Resets last login timestamp
   - `daysLoggedInInARow`: Resets consecutive login streak

- **{discord.Member}** *(optional)*: The Discord user whose stat will be reset
 - Default: If no member specified, resets the command user's own stat

### Permissions
- Requires administrator privileges

### Confirmation Process
- Command prompts for explicit confirmation
- User must type `confirm` within 60 seconds
- Cancels if no confirmation received

### Usage Examples
`!reset xp`           # Resets your own XP
`!reset money @User`  # Resets another user's money balance
`!reset lastLogin`    # Resets your own last login timestamp

### Behavior Details
- Validates requested stat against allowed columns
- Resets stat to database default value
- Uses a secure confirmation mechanism
- Provides detailed error messaging

### Potential Errors
- Insufficient permissions
- Invalid stat specified
- User not found
- Confirmation timeout
## Set Command

### Description
Allows administrators to manually set specific user statistics to precise values with logging support.

### Syntax
`!set {stat}* {value}* {discord.Member}`

### Arguments
- **{stat}** *(required)*: The statistic to modify
 - Supported options:
   - `xp`: Sets user's experience points
   - `money`: Sets user's currency balance

- **{value}** *(required)*: The exact value to set
 - Must be an integer
 - For XP: Compares against current XP to determine level changes
 - For Money: Direct currency amount

- **{discord.Member}** *(optional)*: The Discord user whose stat will be modified
 - Default: If no member specified, modifies the command user's own stat

### Permissions
- Requires administrator privileges

### XP Modification Behavior
- Calculates difference from current XP
- Triggers level up/down events based on XP change
- Preserves level progression mechanics

### Usage Examples
`!set xp 500`         # Sets your own XP to 500
`!set money 1000 @User`  # Sets another user's balance to $1,000
`!set xp 250`         # Sets your own XP to 250

### Error Handling
- Logs errors to admin log channel
- Validates input types
- Prevents invalid stat modifications

### Potential Errors
- Insufficient permissions
- Invalid stat specified
- Non-integer input values
- Database connection issues

#### 3. **Stats Command**
Displays a user’s stats.

- **Syntax**: `!stats {discord.Member}`
- **Arguments**:
  - **{discord.Member}** *(optional)*: The Discord username (e.g., `404_5971` or `ih8tk`). Defaults to displaying your own stats if no member is specified.

#### 4. **Vanity Command**
Displays the bot's statistics, including total lines of code, total commands, and total files.

- **Syntax**: `!vanity`
- **Arguments**: None

#### 5. **ViewCard Command**
View details of a specific card by its name or ID.

- **Syntax**: `!viewCard {query}`
- **Arguments**:
  - **{query}** *(required)*: The card name or ID to view. If the query is numeric, it will search by ID; otherwise, it will search by name.

---

# Function: `updateXpAndCheckLevelUp`

## Description
`updateXpAndCheckLevelUp` is an asynchronous function that updates a Discord user's XP in a database and checks if their level has changed (leveled up or leveled down) based on the updated XP. It handles database interactions, calculates levels using a custom function `xpToLevel`, and sends appropriate notifications to a Discord channel when a level change occurs. The function also manages roles corresponding to levels in the Discord server.

---

## Parameters

### `ctx`
- **Type**: `discord.ext.commands.Context` or `discord.Interaction`
- **Description**: The context of the command or interaction that triggered the function. This is used to identify the user and access the Discord server.

### `bot`
- **Type**: `commands.Bot`
- **Description**: The bot instance used to interact with Discord channels, users, and roles.

### `xp`
- **Type**: `int`, `float`, or `str`
- **Description**: The amount of XP to add or subtract. If a float or string is provided, it will be converted to an integer.

### `add` (optional)
- **Type**: `bool`
- **Default**: `True`
- **Description**: Determines whether to add or subtract XP:
  - `True`: Adds the provided XP to the user's total.
  - `False`: Subtracts the provided XP from the user's total.

---

## Raises

### `ValueError`
- Raised if:
  - `xp` is not a valid integer, float, or string that can be converted to an integer.
  - `add` is not a boolean.

---

## Behavior

1. **XP Validation**: Ensures the provided `xp` is a valid integer. Converts floats and strings as necessary.
2. **User Identification**: Determines the user ID based on the Discord API version.
3. **Database Operations**:
   - Retrieves the current XP for the user from the database.
   - Calculates the user's current level using `xpToLevel`.
   - Updates the user's XP in the database based on the `add` parameter.
   - Recalculates the user's level after the XP update.
4. **Level Change Notifications**:
   - Detects whether the user leveled up or down.
   - Sends a notification to a designated log channel with an embedded message.
5. **Role Management**:
   - Attempts to assign or remove roles corresponding to the user's new level.
   - Sends an admin notification if a required role is missing or if the user already has the role.

---

## Notifications

### Level-Up Notifications
- Sent to the log channel.
- Includes:
  - User's mention (based on conditions).
  - Current level after leveling up.
- Assigns the appropriate role if it exists, or logs an error if it does not.

### Level-Down Notifications
- Sent to the log channel.
- Includes:
  - User's mention (based on conditions).
  - Current level after leveling down.
- Removes the appropriate role if it exists, or logs an error if it does not.

---

## Returns
- **Type**: `None`
- **Description**: The function does not return a value.

---

## Notes
- The function assumes the existence of the following global constants:
  - `LOG_CHANNEL_ID`: The ID of the channel for logging level changes.
  - `ADMIN_LOG_CHANNEL_ID`: The ID of the admin log channel for reporting errors or missing roles.
- The `xpToLevel` function must be implemented separately to handle level calculation logic.


### Additional Information

#### Database Connection
The bot uses a MySQL connection pool to manage database connections efficiently. Ensure that the database configuration is correctly set in the `secret_const.py` file.

#### Font Handling
The bot attempts to use multiple font options for rendering images. If the specified fonts are not found, it falls back to default fonts and logs a warning.

#### Image Generation
The bot uses the OpenAI API to generate card images based on descriptions. Ensure that the `openai_key` is correctly set in the `secret_const.py` file.

#### Error Handling
Commands include error handling to manage common issues, such as missing permissions or invalid input. Ensure that users have the necessary permissions to execute commands.

---

Feel free to use these commands to manage stats efficiently and ensure a balanced experience for everyone!