# Setup

1. In the "**main.py**" script replace "TOKEN" with your Discord bot token.
2. In the "**main.py**" script replace "GUILD_ID" with your Discord server id.

3. In the "**Feedback.py**" script replace "feedback_channel_id" with the Channel, the Feedback gets send in.
4. In the "**FreeGames.py**" script replace "self.channel_id" with the Channel, the Free Games should be sent in.
5. In the "**Moderation.py**" script replace "LOG_CHANNEL_ID" and "self.LOG_CHANNEL_ID" with your log channel.

6. In the "**Notifications.py**" script replace "PUT_ROLE_HERE" with your roles. Also replace: role_id_generalnews, role_id_gameupdates and role_id_socialmedia with your role ids.

- "role1" should be the same role id as "role_id_generalnews" 
- "role2" should be the same role id as "role_id_gameupdates" 
- "role3" should be the same role id as "role_id_socialmedia" 

8. In the "**RolePicker.py**" script change the "role_ids".
9. For "**SteamGamePreview.py**" you need to get your Steam api key. You can follow this tutorial to get your Steam api key: https://www.youtube.com/watch?v=hBqQh5lyQBw

10. For the "**SupportTicket.py**" script you need to change the "report_channel_id" and the "support_channel_id". You can use the same channel id for both of them if you want to. Also you have to change the "moderator_role_id". This is the role, which gets pinged for support tickets.

11. In the "**ThreadManager.py**" script, you need to change the "TARGET_CHANNEL_ID".

12. In the "**YoutubeAnounce.py**" script, you have to change the "self.discord_channel_id".
    | Also you need to replace "@name" with your youtube @.
