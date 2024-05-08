[![discord](https://img.shields.io/badge/contact-me-blue?logo=discord&logoColor=white)](https://discordapp.com/users/499240258114682900)
![Python Versions](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-finished-green)


# Setup

## Project Setup Guide

### Prerequisites
- Ensure you have Python installed on your system.
- You'll need a Discord bot token. If you don't have one, create a bot application on the [Discord Developer Portal](https://discord.com/developers/applications).
- Have the necessary permissions to manage roles and channels on your Discord server.
- Install `"requirements.txt"` packages.
- In Terminal install: `"pip install "py-cord[voice]"`

### Configuration Steps

1. **Token and Guild ID**
   - Open the **main.py** script and replace `"TOKEN"` with your Discord bot token.
   - Replace `"GUILD_ID"` with your Discord server ID.

2. **Feedback Channel Setup**
   - In the **Feedback.py** script, replace `"YOUR_CHANNEL_ID"` with the ID of the channel where feedback should be sent.

3. **Free Games Channel Setup**
   - In the **FreeGames.py** script, replace `"YOUR_CHANNEL_ID"` with the ID of the channel where free game notifications should be sent.

4. **Moderation Log Channel**
   - In the **Moderation.py** script, replace `"LOG_CHANNEL_ID"` and `"self.LOG_CHANNEL_ID"` with the ID of your log channel.

5. **Notification Roles Setup**
   - In the **Notifications.py** script, replace `"PUT_ROLE_HERE"` with the corresponding role IDs.
     - "role1" should match the role id of "role_id_generalnews". (Line 18 & 55)
     - "role2" should match the role id of "role_id_gameupdates". (Line 19 & 56)
     - "role3" should match the role id of "role_id_socialmedia". (Line 20 & 57)

6. **Role Picker Configuration**
   - Modify the "role_ids" in the **RolePicker.py** script to match the roles you want to assign.

7. **Steam API Key**
   - For the **SteamGamePreview.py** script, obtain your Steam API key. Refer to [this tutorial](https://www.youtube.com/watch?v=hBqQh5lyQBw) for guidance.

8. **Support Ticket Setup**
   - In the **SupportTicket.py** script, update the `"report_channel_id"`, `"support_channel_id"`, and `"moderator_role_id"` as needed.

9. **Thread Manager Configuration**
   - Update the `"TARGET_CHANNEL_ID"` in the **ThreadManager.py** script.

10. **YouTube Announcement Setup**
    - In the **YoutubeAnounce.py** script, replace `"self.discord_channel_id"` with the ID of the Discord channel where YouTube announcements should be made.
    - Also, replace "@name" with your YouTube handle.

Once all configurations are complete, run the `"main.py"` script. For further assistance, reach out for support on [discord](https://discord.gg/4xwf8F46Pd).
