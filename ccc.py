import telegram
from telegram import  ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import requests
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Clash of Clans API token
coc_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjZlMjVlNzUwLWU4YWMtNDViZS04ZTczLTBjNjRjODgzYTBlMCIsImlhdCI6MTcxNDI0MTU3Niwic3ViIjoiZGV2ZWxvcGVyLzBmZDRhZGYzLTU0YmYtNTYyMi0wNzAyLTJjY2ZiN2VlZTI4YiIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjE2Ny43MS4zMy4xOTgiXSwidHlwZSI6ImNsaWVudCJ9XX0.b8DcOMjUqMLSBFaNtZxaww_QhwS6x1L34DjEWBdT7XwF4UtDV4NaEq7UYeau8KSzDCf-MNDhwCWcH12w0MehaQ'

# Telegram Bot token
telegram_token = '7026234380:AAE9DfI8H-Tz6KSi3hClgL4zIAKCgQGSiLk'

group_invite_link = 'https://t.me/+KyaNqnyIO6I3MjU8'

# List of allowed group IDs
group_id = ['-4031622087']

# Function to check if a user is a member of the allowed group
def is_member(update):
 return True


# Function to get player information from Clash of Clans API
def get_player_info(player_tag):
    # Ensure the player tag is correctly formatted
    player_tag = urllib.parse.quote(player_tag)

    url = f"https://api.clashofclans.com/v1/players/{player_tag}"
    headers = {"Authorization": f"Bearer {coc_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        return response.json()  # Return the JSON response if the request was successful
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Print the HTTP error
    except Exception as err:
        print(f"An error occurred: {err}")  # Print any other error

    return None  # Return None if there was an error


def generate_player_thumbnail(player_info):
    # Load background image
    background_image_path = "background.jpg"  # Path to your background image
    background_image = Image.open(background_image_path)

    # Resize background image to match thumbnail size
    img_width, img_height = 1080, 1920
    background_image = background_image.resize((img_width, img_height))

    # Create a drawing object
    draw = ImageDraw.Draw(background_image)

    # Load a custom font (replace 'path_to_your_font.ttf' with the actual path to your font file)
    font_path = "font.ttf"
    font_size = 50
    font = ImageFont.truetype(font_path, font_size)

    # Define player and clan text
    player_text = f"\n\n\n\n\n{player_info['name']}\n" \
                  f"{player_info['role']}\n" \
                  f"Experience Level: {player_info['expLevel']}\n\n\n\n\n\n\n\n\n\n\n\n\n" \
                  f"TH: {player_info.get('townHallWeaponLevel', 'N/A')}\n" \
                  f"trophies: {player_info.get('trophies', 'N/A')}\n" \
                  f"war stars: {player_info.get('warStars', 'N/A')}"

    clan_text = f"                                      Clan\n" \
                f"Name: {player_info['clan'].get('name', 'N/A')}\n" \
                f"Tag: {player_info['clan'].get('tag', 'N/A')}\n" \
                f"Lvl: {player_info['clan'].get('clanLevel', 'N/A')}"

    # Define text positions and margins
    left_margin = 20
    top_margin = 150
    line_spacing = 10
    player_top = top_margin
    clan_top = img_height // 2 + top_margin

    # Load fonts with respective sizes
    normal_font_size = 50
    normal_font = ImageFont.truetype(font_path, normal_font_size)

    # Draw player text
    for line in player_text.split('\n'):
        draw.text((left_margin, player_top), line, fill="#ffd700", font=normal_font)
        player_top += normal_font.getsize(line)[1] + line_spacing

    # Draw "Clan" line with font size 100
    draw.text((left_margin, clan_top), "                   Clan\n\n", fill="#FFB200", font=ImageFont.truetype(font_path, 100))
    clan_top += 100 + line_spacing

    # Draw remaining clan text
    for line in clan_text.split('\n')[1:]:  # Exclude the "Clan" line
        draw.text((left_margin, clan_top), line, fill="#ffd700", font=normal_font)
        clan_top += normal_font.getsize(line)[1] + line_spacing


    # Save the image to a BytesIO object
    img_byte_array = BytesIO()
    background_image.save(img_byte_array, format="PNG")
    img_byte_array.seek(0)

    return img_byte_array


def player(update, context, player_tag=None):
    if not player_tag:
        if len(context.args) == 0:
            update.message.reply_text("Please provide a player tag. Example usage: /player #PLAYER_TAG")
            return
        player_tag = context.args[0]
    
    player_info = get_player_info(player_tag)

    if player_info:
        # Generate thumbnail image with player information
        thumbnail_image = generate_player_thumbnail(player_info)

        # Create the inline keyboard markup
        keyboard = [[InlineKeyboardButton("Go to player's profile", url=f'https://link.clashofclans.com/en/?action=OpenPlayerProfile&tag={player_tag[1:]}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Format player information as a string
        player_name = player_info.get('name', 'N/A')
        player_role = player_info.get('role', 'N/A')
        player_league = player_info.get('league', {}).get('name', 'N/A')

        # Check if the player is in a clan
        if 'clan' in player_info:
            clan_name = player_info['clan'].get('name', 'Not in a clan')
            clan_tag = player_info['clan'].get('tag', 'N/A')
            clan_level = player_info['clan'].get('clanLevel', 'N/A')
            clan_info = f"Clan Name: {clan_name}\nClan Tag: {clan_tag}\nClan Level: {clan_level}\n"

        # Format player information as a string
        player_info_str = f"Player Info:\nPlayer Name: {player_name}\nPlayer Role: {player_role}\n"

        # Add clan information if the player is in a clan
        if 'clan' in player_info:
            player_info_str += clan_info

        player_info_str += f"Player League: {player_league}\n\n"

        player_info_str += "Attacks:\n"
        player_info_str += f"Town Hall Level: {player_info.get('townHallLevel', 'N/A')}\n"
        player_info_str += f"Town Hall Weapon Level: {player_info.get('townHallWeaponLevel', 'N/A')}\n"
        player_info_str += f"Builder Hall Level: {player_info.get('builderHallLevel', 'N/A')}\n"
        player_info_str += f"Builder Base Trophies: {player_info.get('builderBaseTrophies', 'N/A')}\n"
        player_info_str += f"Trophies: {player_info.get('trophies', 'N/A')}\n"
        player_info_str += f"Experience Level: {player_info.get('expLevel', 'N/A')}\n"
        player_info_str += f"War Stars: {player_info.get('warStars', 'N/A')}\n"
        player_info_str += f"Attack Wins: {player_info.get('attackWins', 'N/A')}\n"
        player_info_str += f"Defense Wins: {player_info.get('defenseWins', 'N/A')}\n\n"

        player_info_str += "Donates:\n"
        player_info_str += f"Donated: {player_info.get('donations', 'N/A')}\n"
        player_info_str += f"Received: {player_info.get('donationsReceived', 'N/A')}\n\n"

        # Send the thumbnail image along with the inline keyboard and player information
        context.bot.send_photo(update.message.chat_id, photo=thumbnail_image, reply_markup=reply_markup, caption=player_info_str, parse_mode='HTML')
    else:
        update.message.reply_text("Player information not found or an error occurred.")


# Function to get player troops information from Clash of Clans API
def get_player_troops(player_tag):
    # Ensure the player tag is correctly formatted
    player_tag = urllib.parse.quote(player_tag)

    url = f"https://api.clashofclans.com/v1/players/{player_tag}"
    headers = {"Authorization": f"Bearer {coc_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        return response.json()  # Return the JSON response if the request was successful
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Print the HTTP error
    except Exception as err:
        print(f"An error occurred: {err}")  # Print any other error

    return None  # Return None if there was an error

# Function to handle /player_troops command
def player_troops(update, context, player_tag=None):
    if not player_tag:
        if len(context.args) == 0:
            update.message.reply_text("Please provide a player tag. Example usage: /player_troops #PLAYER_TAG")
            return
        player_tag = context.args[0]
    
    player_troops_info = get_player_troops(player_tag)
    
    if player_troops_info:
        troops_info = player_troops_info.get('troops', [])
        if troops_info:
            troops_str = "Player Troops Info:\n"
            for troop in troops_info:
                troop_name = troop.get('name', 'Unknown')
                troop_level = troop.get('level', 'Unknown')
                troop_max_level = troop.get('maxLevel', 'Unknown')
                troop_info_str = f"\nTroop Name: {troop_name}\nTroop Level: {troop_level}\nTroop Max Level: {troop_max_level}\n"
                
                # Check if adding the current troop info will exceed the message length limit
                if len(troops_str + troop_info_str) > telegram.constants.MAX_MESSAGE_LENGTH:
                    # Send the accumulated troops string
                    update.message.reply_text(troops_str)
                    # Reset the troops string for the next batch
                    troops_str = "Player Troops Info (Continued):\n"
                
                # Append the current troop info to the accumulated troops string
                troops_str += troop_info_str
            
            # Send any remaining troops
            if troops_str:
                update.message.reply_text(troops_str)
        else:
            update.message.reply_text("No troop information found for this player.")
    else:
        update.message.reply_text("Player troop information not found or an error occurred.")

# Function to get player achievements information from Clash of Clans API
def get_player_achievements(player_tag):
    # Ensure the player tag is correctly formatted
    player_tag = urllib.parse.quote(player_tag)

    url = f"https://api.clashofclans.com/v1/players/{player_tag}"
    headers = {"Authorization": f"Bearer {coc_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        return response.json()  # Return the JSON response if the request was successful
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Print the HTTP error
    except Exception as err:
        print(f"An error occurred: {err}")  # Print any other error

    return None  # Return None if there was an error

# Function to handle /player_achievements command
def player_achievements(update, context, player_tag):
    if not player_tag:
        update.message.reply_text("Please provide a player tag. Example usage: /player_achievements #PLAYER_TAG")
        return
    
    player_achievements_info = get_player_achievements(player_tag)
    
    if player_achievements_info:
        achievements_info = player_achievements_info.get('achievements', [])
        if achievements_info:
            achievements_str = "Player Achievements Info:\n"
            for achievement in achievements_info:
                achievement_name = achievement.get('name', 'Unknown')
                achievement_stars = achievement.get('stars', 'Unknown')
                achievement_value = achievement.get('value', 'Unknown')
                achievement_target = achievement.get('target', 'Unknown')
                achievement_info = achievement.get('info', 'Unknown')
                achievement_completion_info = achievement.get('completionInfo', 'Unknown')
                achievement_text = f"\nAchievement Name: {achievement_name}\nAchievement Stars: {achievement_stars}\n"
                achievement_text += f"Achievement Value: {achievement_value}\nAchievement Target: {achievement_target}\n"
                achievement_text += f"Achievement Info: {achievement_info}\n"
                achievement_text += f"Achievement Completion Info: {achievement_completion_info}\n"
                
                # Check if adding the next achievement will exceed the maximum message length
                if len(achievements_str) + len(achievement_text) > telegram.constants.MAX_MESSAGE_LENGTH:
                    update.message.reply_text(achievements_str)
                    achievements_str = "Continuation of Player Achievements Info:\n"  # Start a new message for the next achievements
                achievements_str += achievement_text
            
            # Send the last part of achievements
            update.message.reply_text(achievements_str)
        else:
            update.message.reply_text("No achievement information found for this player.")
    else:
        update.message.reply_text("Player achievement information not found or an error occurred.")

# Function to get clan information from Clash of Clans API
def get_clan_info(clan_tag):
    # Ensure the clan tag is correctly formatted
    clan_tag = urllib.parse.quote(clan_tag)

    url = f"https://api.clashofclans.com/v1/clans/{clan_tag}"
    headers = {"Authorization": f"Bearer {coc_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        clan_info = response.json()  # Get the JSON response
        return clan_info  # Return the clan information
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Print the HTTP error
    except Exception as err:
        print(f"An error occurred: {err}")  # Print any other error

    return None  # Return None if there was an error

def generate_clan_thumbnail(clan_info):
    # Load background image
    background_image_path = "clan_background.jpg"  # Path to your background image
    background_image = Image.open(background_image_path)

    # Resize background image to match thumbnail size
    img_width, img_height = 1080, 1920
    background_image = background_image.resize((img_width, img_height))

    # Create a drawing object
    draw = ImageDraw.Draw(background_image)

    # Load a custom font (replace 'path_to_your_font.ttf' with the actual path to your font file)
    font_path = "font.ttf"
    font_size = 50
    font = ImageFont.truetype(font_path, font_size)
    bold_font = ImageFont.truetype(font_path, font_size * 2)

    # Define text positions
    left_margin = 60
    top_margin = 0  # Adjusted top margin

    # Define text in silver
    silver_text = [
        f"Name: {clan_info['name']}",
        f"LVL: {clan_info.get('clanLevel', 'Unknown')}",
        f"Points: {clan_info.get('clanPoints', 'Unknown')}",
        f"Type: {clan_info.get('type', 'Unknown')}",
        f"Builder Base: {clan_info.get('clanBuilderBasePoints', 'Unknown')}",
        f"Capital Points: {clan_info.get('clanCapitalPoints', 'Unknown')}",
        f"Family Friendly: {clan_info.get('isFamilyFriendly', False)}"
    ]

    # Calculate the total height of the text block
    total_text_height = bold_font.getsize("Clan\n\n")[1] + sum(font.getsize(line)[1] for line in silver_text)

    # Calculate the top margin to center the text vertically
    top_margin = (img_height - total_text_height) // 2

    # Draw "Clan" line with font size 100
    draw.text((left_margin, top_margin), "                 Clan\n\n", fill="#FFB200", font=bold_font)

    # Draw text in silver
    current_height = top_margin + bold_font.getsize("Clan\n\n")[1]
    for line in silver_text:
        draw.text((left_margin, current_height), line, fill="#ffd700", font=font)
        current_height += font.getsize(line)[1]  # Update current height

    # Save the image to a BytesIO object
    img_byte_array = BytesIO()
    background_image.save(img_byte_array, format="PNG")
    img_byte_array.seek(0)

    return img_byte_array


# Function to handle /clan command
def clan(update, context, clan_tag=None):
    if not clan_tag:
        if len(context.args) == 0:
            update.message.reply_text("Please provide a clan tag. Example usage: /clan #CLAN_TAG")
            return
        clan_tag = context.args[0]
    
    try:
        clan_info = get_clan_info(clan_tag)
        if clan_info and 'name' in clan_info:
            # Generate thumbnail image with clan information
            thumbnail_image = generate_clan_thumbnail(clan_info)

            # Create the inline keyboard markup
            keyboard = [[InlineKeyboardButton("Go to clan's profile", url=f'https://link.clashofclans.com/en/?action=OpenClanProfile&tag={clan_tag[1:]}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Format clan information as a string
            clan_name = clan_info.get('name', 'N/A')
            clan_level = clan_info.get('clanLevel', 'Unknown')
            clan_members = clan_info.get('members', 'Unknown')
            clan_points = clan_info.get('clanPoints', 'Unknown')
            clan_type = clan_info.get('type', 'Unknown')
            clan_description = clan_info.get('description', 'Unknown')
            clan_builder_base_points = clan_info.get('clanBuilderBasePoints', 'Unknown')
            clan_capital_points = clan_info.get('clanCapitalPoints', 'Unknown')
            is_family_friendly = clan_info.get('isFamilyFriendly', False)
            war_frequency = clan_info.get('warFrequency', 'Unknown')
            war_win_streak = clan_info.get('warWinStreak', 'Unknown')
            war_wins = clan_info.get('warWins', 'Unknown')
            war_ties = clan_info.get('warTies', 'Unknown')
            war_losses = clan_info.get('warLosses', 'Unknown')
            is_war_log_public = clan_info.get('isWarLogPublic', 'Unknown')
            capital_league_info = clan_info.get('capitalLeague', {})
            war_league_info = clan_info.get('warLeague', {})
            
            # Construct clan information string
            clan_info_str = f"Clan Info:\n"
            clan_info_str += f"Clan Name: {clan_name}\n"
            clan_info_str += f"Clan Level: {clan_level}\n"
            clan_info_str += f"Clan Members: {clan_members}\n"
            clan_info_str += f"Clan Points: {clan_points}\n"
            clan_info_str += f"Clan Type: {clan_type}\n"
            clan_info_str += f"Clan Description: {clan_description}\n\n"
            clan_info_str += f"Clan Builder Base Points: {clan_builder_base_points}\n"
            clan_info_str += f"Clan Capital Points: {clan_capital_points}\n"
            clan_info_str += f"Is Family Friendly: {is_family_friendly}\n\n"
            clan_info_str += "Clan Wars:\n"
            clan_info_str += f"War Wins: {war_wins}\n"
            clan_info_str += f"War Losses: {war_losses}\n"
            clan_info_str += f"War Ties: {war_ties}\n"
            clan_info_str += f"War Win Streak: {war_win_streak}\n"
            clan_info_str += f"War Frequency: {war_frequency}\n"
            clan_info_str += f"Is War Log Public: {is_war_log_public}\n\n"
            
            if war_league_info:
                clan_info_str += "War League:\n"
                clan_info_str += f"War League Name: {war_league_info.get('name', 'Unknown')}\n"
                clan_info_str += f"War League ID: {war_league_info.get('id', 'Unknown')}\n\n"
            
            if capital_league_info:
                clan_info_str += "Capital League:\n"
                clan_info_str += f"Capital League Name: {capital_league_info.get('name', 'Unknown')}\n"
                clan_info_str += f"Capital League ID: {capital_league_info.get('id', 'Unknown')}\n"

            # Send the thumbnail image along with the clan information and the inline keyboard
            context.bot.send_photo(update.message.chat_id, photo=thumbnail_image, caption=clan_info_str, reply_markup=reply_markup, parse_mode='HTML')
        elif clan_info:
            update.message.reply_text("This clan is set to private, so I cannot retrieve detailed information.")
        else:
            update.message.reply_text("Clan information not found or an error occurred.")
    except TimeoutError:
        update.message.reply_text("The request to the Clash of Clans API timed out. Please try again later.")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")


# Function to get league information from Clash of Clans API
def get_league_info(league_id):
    url = f"https://api.clashofclans.com/v1/leagues/{league_id}"
    headers = {"Authorization": f"Bearer {coc_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        league_info = response.json()
        return league_info.get('name')  # Return the league name from the JSON response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Print the HTTP error
    except Exception as err:
        print(f"An error occurred: {err}")  # Print any other error

    return None  # Return None if there was an error

# Function to handle /league command
def league(update, context, league_id=None):
    if not league_id:
        if len(context.args) == 0:
            update.message.reply_text("Please provide a league ID. Example usage: /league 29000011")
            return
        league_id = context.args[0]
    
    league_name = get_league_info(league_id)
    
    if league_name:
        update.message.reply_text(f"League Name: {league_name}")
    else:
        update.message.reply_text("League information not found or an error occurred.")

# Function to get clan members from Clash of Clans API
def get_clan_members(clan_tag):
    # Ensure the clan tag is correctly formatted
    clan_tag = urllib.parse.quote(clan_tag)

    url = f"https://api.clashofclans.com/v1/clans/{clan_tag}/members"
    headers = {"Authorization": f"Bearer {coc_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        return response.json()  # Return the JSON response if the request was successful
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Print the HTTP error
    except Exception as err:
        print(f"An error occurred: {err}")  # Print any other error

    return None  # Return None if there was an error

# Function to handle /clan_members command
def clan_members(update, context, clan_tag=None):
    if not clan_tag:
        if len(context.args) == 0:
            update.message.reply_text("Please provide a clan tag. Example usage: /clan_members #CLAN_TAG")
            return
        clan_tag = context.args[0]
    
    clan_members_data = get_clan_members(clan_tag)
    
    if clan_members_data and 'items' in clan_members_data:
        members = clan_members_data['items']
        members_info = []
        for member in members:
            member_name = member.get('name', 'Unknown')
            member_role = member.get('role', 'Unknown')
            member_id = member.get('tag', 'Unknown')
            member_info = f"Member Name: {member_name}\nMember Role: {member_role}\nMember ID: {member_id}\n"
            members_info.append(member_info)
        members_str = "\n\n".join(members_info)
        update.message.reply_text("Clan Members:\n" + members_str)
    else:
        update.message.reply_text("Clan members not found or an error occurred.")


# Function to get information about clan's current clan war
def get_current_war(clan_tag, coc_token):
    # Ensure the clan tag is correctly formatted
    clan_tag = urllib.parse.quote(clan_tag)

    url = f"https://api.clashofclans.com/v1/clans/{clan_tag}/currentwar"
    headers = {"Authorization": f"Bearer {coc_token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        return response.json()  # Return the JSON response if the request was successful
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Print the HTTP error
    except Exception as err:
        print(f"An error occurred: {err}")  # Print any other error

    return None  # Return None if there was an error

# Function to handle /current_war command
def current_war(update, context, clan_tag=None):
    if not clan_tag:
        if len(context.args) == 0:
            update.message.reply_text("Please provide a clan tag. Example usage: /current_war #CLAN_TAG")
            return
        clan_tag = context.args[0]
    
    war_info = get_current_war(clan_tag, coc_token)
    if war_info:
        state = war_info.get('state', 'Unknown')
        clan_info = war_info.get('clan', {})
        opponent_info = war_info.get('opponent', {})
        
        message = f"In War: {state}\n\n"
        
        message += "Clan Info:\n"
        message += f"Clan Level: {clan_info.get('clanLevel', 'Unknown')}\n"
        message += f"Clan Attacks: {clan_info.get('attacks', 'Unknown')}\n"
        message += f"Clan Stars: {clan_info.get('stars', 'Unknown')}\n"
        message += f"Clan Destruction Percentage: {clan_info.get('destructionPercentage', 'Unknown')}%\n\n"
        
        message += "Opponent Info:\n"
        message += f"Opponent Level: {opponent_info.get('clanLevel', 'Unknown')}\n"
        message += f"Opponent Attacks: {opponent_info.get('attacks', 'Unknown')}\n"
        message += f"Opponent Stars: {opponent_info.get('stars', 'Unknown')}\n"
        message += f"Opponent Destruction Percentage: {opponent_info.get('destructionPercentage', 'Unknown')}%\n"
        
        update.message.reply_text(message)
    else:
        update.message.reply_text("War information not found or an error occurred.")

# Function to start the bot and display a welcome message
def start(update, context):
    user_name = update.effective_user.first_name
    if is_member(update):
        update.message.reply_text(f"Hello {user_name}, how can I help you? Please use /help to see available commands.")
    else:
        update.message.reply_text(f"Hello {user_name}, to be able to use our bot, you need to join our group {group_invite_link}, then come back here and click /start")

# Function to handle button clicks
def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    # Get the callback data which corresponds to the button clicked
    callback_data = query.data

    # Get the corresponding command function based on the callback data
    command_function = button_callbacks.get(callback_data)

    # If the command function exists, prompt the user to provide a tag
    if command_function:
        # Store the command function in context for later use
        context.user_data['command_function'] = command_function
        query.message.reply_text(f"Please provide the {callback_data} tag:")

# Dictionary to map button callbacks to corresponding command functions
button_callbacks = {
    'player': player,
    'player_troops': player_troops,
    'player_achievements': player_achievements,
    'clan': clan,
    'clan_members': clan_members,
    'current_war': current_war,
    'league': league,
    'help': help
}

# Function to create and send the menu with buttons
def send_menu(update, context):
    # Define the buttons for each command
    buttons = [
        [InlineKeyboardButton("Player", callback_data='player')],
        [InlineKeyboardButton("Player Troops", callback_data='player_troops')],
        [InlineKeyboardButton("Player Achievements", callback_data='player_achievements')],
        [InlineKeyboardButton("Clan", callback_data='clan')],
        [InlineKeyboardButton("Clan Members", callback_data='clan_members')],
        [InlineKeyboardButton("Current War", callback_data='current_war')],
        [InlineKeyboardButton("League", callback_data='league')]
    ]

    # Create a keyboard markup with the menu buttons
    reply_markup = InlineKeyboardMarkup(buttons)

    # Send the menu message with the keyboard
    update.message.reply_text("Choose an option:", reply_markup=reply_markup)

def handle_tag(update: Update, context: CallbackContext):
    # Check if the message is a command
    if update.message.text.startswith('/'):
        tag = update.message.text
        command_function = context.user_data.get('command_function')

        if command_function:
            # Call the command function directly with the tag
            command_function(update, context, tag)
        else:
            update.message.reply_text("No command function found. Please click a button to start.")
    # Check if the message is a reply to the bot's message
    elif update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id:
        tag = update.message.text
        command_function = context.user_data.get('command_function')

        if command_function:
            # Call the command function directly with the tag
            command_function(update, context, tag)
        else:
            update.message.reply_text("No command function found. Please click a button to start.")

# Main function
def main():
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("clash", send_menu))

    # Add button click handler to dispatcher
    dispatcher.add_handler(CallbackQueryHandler(button_click))

    # Add message handler to dispatcher to handle user input after button click
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_tag))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()


