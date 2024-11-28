# Omniplexium-Eternal: Admin Commands Guide

Welcome to the admin commands guide for Omniplexium-Eternal! Below you'll find detailed instructions on using commands to manage user stats, including resetting, setting values, and viewing stats. Required arguments are marked with an asterisk (*).

---

### Commands Overview

- **`!reset`** - Reset a user’s stat
- **`!set`** - Set a specific stat to a given value
- **`!stats`** - Display a user’s stats
- **`!vanity`** - Display bot statistics
- **`!viewCard`** - View details of a specific card

---

### Command Details

#### 1. **Reset Command**
Reset a specific stat for a user.

- **Syntax**: `!reset {stat}* {discord.Member}`
- **Arguments**:
  - **{stat}** *(required)*: The stat to reset. Options:
    - `xp`
    - `money`
  - **{discord.Member}** *(optional)*: The Discord username (e.g., `404_5971` or `ih8tk`). Defaults to your own stats if no member is specified.

#### 2. **Set Command**
Set a specific stat to a given integer value for a user.

- **Syntax**: `!set {stat}* {value}* {discord.Member}`
- **Arguments**:
  - **{stat}** *(required)*: The stat to set. Options:
    - `xp`
    - `money`
  - **{value}** *(required)*: Any integer value, such as `1`, `3`, or `45`.
  - **{discord.Member}** *(optional)*: The Discord username (e.g., `404_5971` or `ih8tk`). Defaults to your own stats if no member is specified.

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