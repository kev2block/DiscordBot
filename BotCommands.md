## AI Chat Command

**Description:**
Interact with an AI model to ask questions or engage in conversation. The AI model provides responses based on the input query. Utilizes a pre-trained AI model.

**Available Commands:**
- `/AIChat <query>`: Initiates a conversation with the AI model.

## Feedback Command

**Description:**
Allows users to submit feedback through a button-triggered modal interface. Feedback includes a title, Discord username, and message.

**Available Commands:**
- `!feedback`: Creates a modal interface for submitting feedback.

## Free Games Command

**Description:**
This command monitors and posts updates about free games available on the Epic Games Store. It periodically checks for new free game promotions and notifies the specified channel about them.

**Available Commands:**
- `/PostCurrentFreeGames`: Manually posts the current free games available on the Epic Games Store.

## Giveaway Command

**Description:**
Start, manage, and end giveaways within Discord servers using this command. Users can join giveaways, and winners are randomly selected when the giveaway ends.

**Available Commands:**
- `/giveaway <time> <winners> <prize>`: Starts a new giveaway with the specified duration (in seconds), number of winners, and prize.
- `/giveawayreroll <message_id> <winners>`: Rerolls winners for a specific ended giveaway with the given message ID. 

## Help Command

**Description:**
Displays help information for all available commands supported by the bot.

**Available Commands:**
- `/help`: Displays information about various commands available in the bot.

## Moderation Commands

**Description:**
This module provides commands for moderating server activities, such as warnings, kicks, bans, mutes, message deletion, and handling user requests.

**Available Commands:**
- `/warnings`: Displays the number of warnings for a specified user.
- `/kick`: Kicks a specified member from the server.
- `/ban`: Bans a specified member from the server.
- `/mute`: Mutes a specified member for a specified duration. (timeout)
- `/warn`: Warns a user for specified reasons and handles suspension for repeated infractions.
- `/clear`: Clears a specified number of messages from the channel.
- `/userclear`: Clears a specified number of messages from the selected user.

## Music Command

**Description:**
Allows users to play music from YouTube in voice channels.

**Available Commands:**
- `/play <query>`: Plays a selected song from YouTube.
- `/pause`: Pauses the current song being played.
- `/resume` or `/r`: Resumes playing the current song.
- `/skip` or `/s`: Skips the current song being played.
- `/queue` or `/q`: Displays the current songs in queue.
- `/clear` or `/c` or `/bin`: Stops the music and clears the queue.
- `/stop` or `/disconnect` or `/leave` or `/d`: Disconnects the bot from the voice channel.
- `/remove <index>`: Removes the specified song from the queue.

## Notifications Command

**Description:**
Enables server administrators to manage notification settings interactively. Users can toggle notifications for updates like YouTube videos, game releases, and social media posts through an interactive interface.

## Notifications Command

**Description:**
Manage user notification settings for YouTube videos, game updates, and social media posts.

**Available Commands:**
- `/roles`: Displays notification settings with toggle options via interactive buttons. 

## Role Picker Command

**Description:**
Allows users to select a role based on color through an interactive button interface. Useful for visual organization or access management in Discord servers.

**Available Commands:**
- `/RolePick`: Presents an embed with color-coded buttons allowing users to pick a role. Each button corresponds to a different role color like Green, Blue, Red, Purple, and Yellow.

## Show All Roles Command

**Description:**
This command allows users to view all their roles in the Discord server. It provides a user-friendly interface with a button that users can click to display their roles in an embed.

**Available Commands:**
- `/role`: Sends an embed with a button labeled "Show Roles". When clicked, it lists all the roles assigned to the user, excluding the default "@everyone" role.

## Steam Game Preview Command

**Description:**
Allows users to retrieve detailed information about Steam games, including price, release date, developer, and tags, by using the game's name.

**Available Commands:**
- `/gameinfo <game_name>`: Searches for a Steam game by name and displays detailed information in an embed. If no exact match is found or the game's details are unavailable, the command provides feedback accordingly.

## Support Ticket Command

**Description:**
Enables users to open support tickets for various issues or inquiries within the Discord server. The command features an interactive menu allowing users to choose from several options including reporting a user, applying for a moderator role, and other miscellaneous queries.

**Available Commands:**
- `/support`: Displays an interactive view allowing users to select the type of ticket they want to open. Options include application for roles, user reporting, and miscellaneous inquiries. This command embeds detailed instructions for reporting and emphasizes appropriate use of the ticket system.

## Thread Manager Command

**Description:**
Automatically manages threads in a specific channel based on incoming messages. Creates threads for new messages and can handle thread lifecycle, such as archiving or deleting threads after a set period.

**Available Commands:**
- There are no direct commands for this functionality. It operates automatically when messages are sent to the specified channel (`TARGET_CHANNEL_ID`).

## YouTube Announce Command

**Description:**
Automatically announces new YouTube videos from specified channels in a Discord channel. This cog continuously checks for new videos every minute and sends an update message to the designated Discord channel when a new video is found.

**Features:**
- **Automatic Video Checks**: Checks linked YouTube channels every minute for new video uploads.
- **Announcement of New Videos**: Posts a message in a specific Discord channel when a new video is detected.
- **Error Handling**: Logs errors if there are issues fetching new videos from YouTube.

