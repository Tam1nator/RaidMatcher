from flask import Flask
import threading
import discord
from discord.ext import commands
from discord import app_commands

# Flask app setup
app = Flask(__name__)

# Discord bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='/', intents=intents)

bot_running = False
bot_error_message = None

# Variables to store the channels in which commands are allowed
player_search_channel_id = None
clan_search_channel_id = None

# Bot event and command setup
@bot.event
async def on_ready():
    global bot_running, bot_error_message
    bot_running = True
    bot_error_message = None
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_disconnect():
    global bot_running, bot_error_message
    bot_running = False
    bot_error_message = "Bot disconnected unexpectedly."
    print(bot_error_message)

def is_bot_manager():
    async def predicate(interaction: discord.Interaction):
        return any(role.name == "Bot Manager" for role in interaction.user.roles)
    return commands.check(predicate)

def is_special_user(interaction):
    if interaction.user.id == 649571921633083412:
        return interaction.user.guild_permissions.administrator
    return False

@app_commands.guilds(discord.Object(id=1213279065306431588))
@bot.tree.command(name="set_channel", description="Set the channels where commands are allowed")
@is_bot_manager()
async def set_channel(interaction: discord.Interaction, player_search: discord.TextChannel, clan_search: discord.TextChannel):
    global player_search_channel_id, clan_search_channel_id
    player_search_channel_id = player_search.id
    clan_search_channel_id = clan_search.id
    await interaction.response.send_message(f'Player search commands are now restricted to {player_search.mention}. Clan search commands are now restricted to {clan_search.mention}.')

def check_player_search_channel(interaction):
    return player_search_channel_id and interaction.channel_id == player_search_channel_id

def check_clan_search_channel(interaction):
    return clan_search_channel_id and interaction.channel_id == clan_search_channel_id

@app_commands.guilds(discord.Object(id=1213279065306431588))
@bot.tree.command(name="open_raid_post", description="Create a Raid Matcher post")
@app_commands.choices(
    skill_level=[
        app_commands.Choice(name="Amateur", value="Amateur"),
        app_commands.Choice(name="Experienced", value="Experienced"),
        app_commands.Choice(name="Professional", value="Professional")
    ],
    cg_donation=[
        app_commands.Choice(name="0%", value="0%"),
        app_commands.Choice(name="25%", value="25%"),
        app_commands.Choice(name="50%", value="50%"),
        app_commands.Choice(name="75%", value="75%"),
        app_commands.Choice(name="100%", value="100%")
    ]
)
async def open_raid_post(
    interaction: discord.Interaction,
    clan_tag: str,
    available_slots: int,
    skill_level: str,
    contact: str,
    cg_donation: str,
    extra_info: str = "No"
):
    if not check_player_search_channel(interaction):
        await interaction.response.send_message("This command is not allowed in this channel.")
        return

    embed = discord.Embed(title="Raid Matcher - Open Raid Spots", color=discord.Color.gold())
    embed.add_field(name="Clan Tag", value=clan_tag, inline=False)
    embed.add_field(name="Available Slots", value=str(available_slots), inline=False)
    embed.add_field(name="Skill Level", value=skill_level, inline=False)
    embed.add_field(name="Contact", value=contact, inline=False)
    embed.add_field(name="CG Donation", value=cg_donation, inline=False)
    embed.add_field(name="Additional Info", value=extra_info, inline=False)
    await interaction.response.send_message(embed=embed)

# Flask route definitions
@app.route('/')
def home():
    if bot_running:
        return "Hello from Flask! The Discord bot is running and connected."
    elif bot_error_message:
        return f"Hello from Flask! The Discord bot is not running. Error: {bot_error_message}"
    else:
        return "Hello from Flask! The Discord bot is not running and no specific error message is available."

# Function to run the Discord bot
def run_discord_bot():
    try:
        bot.run('MTIzMzQyNjEzMTU4NDAyODY4Mg.GWnwM7.KRMxEED0G60HeEol04UDvkzIGCU5-RkbCnt_oo')  # Replace 'YOUR_BOT_TOKEN' with your actual Discord bot token.
    except Exception as e:
        global bot_running, bot_error_message
        bot_running = False
        bot_error_message = str(e)  # Store the error message
        print(f"Failed to start the bot: {e}")

# Main block to run the Flask app and Discord bot in separate threads
if __name__ == "__main__":
    # Running the Discord bot in a separate thread
    bot_thread = threading.Thread(target=run_discord_bot, daemon=True)
    bot_thread.start()
    # Running the Flask app
    app.run(port=5001, debug=True)
