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