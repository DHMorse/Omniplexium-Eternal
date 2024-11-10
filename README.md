# Omniplexium-Eternal: Admin Commands Guide

Welcome to the admin commands guide for Omniplexium-Eternal! Below you'll find detailed instructions on using commands to manage user stats, including resetting, setting values, and viewing stats. Required arguments are marked with an asterisk (*).

---

### Commands Overview

- **`!reset`** - Reset a user’s stat
- **`!set`** - Set a specific stat to a given value
- **`!stats`** - Display a user’s stats

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

---

Feel free to use these commands to manage stats efficiently and ensure a balanced experience for everyone!
