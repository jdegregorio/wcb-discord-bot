# Discord Bot for Will Carter League of Champions
Discord bot for our long-running fantasy football league discord server.

### Setting up Environment Variables

For this bot to run, you need to setup a `.env` file that contains all of the required tokens.

Contents:
```
DISCORD_TOKEN=<YOUR TOKEN GOES HERE>

```

### Installing on Discord

To install this bot on your discord server, use the following invite link:

https://discord.com/oauth2/authorize?client_id=<YOUR_CLIENT_ID>&scope=bot&permissions=535261346880


### General Instructions for Creating Discord App

To set up the Discord bot, you need to create a bot account, get the token, and then invite the bot to your server. 

Here's a step-by-step guide:

1. Go to the Discord Developer Portal: https://discord.com/developers/applications

1. Log in with your Discord account.

1. Click on the "New Application" button in the top-right corner.

1. Enter a name for your application, then click "Create."

1. You will be redirected to the "General Information" page for your application. On the left sidebar, click on "Bot."

1. Click on the "Add Bot" button, and then confirm by clicking "Yes, do it!".

1. You should now see the bot's information. To get the bot token, click on the "Copy" button next to the "Token" field. This token will be used in your Python code to authorize your bot. Make sure not to share this token, as it allows full control of your bot.

1. To invite the bot to your Discord server, go back to the "General Information" page by clicking on it in the left sidebar.

1. Under the "Client ID" field, click on the "Copy" button.

1. Replace YOUR_CLIENT_ID in the following URL with the copied client ID:

`https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&scope=bot&permissions=8`

1. Open the modified URL in your browser, and you will be prompted to select a server to invite the bot to. Choose the desired server and click "Authorize."

1. You may need to complete a captcha to confirm the invitation. Once completed, your bot should be added to the server.

**Remember to add the bot token to your .env file**

 