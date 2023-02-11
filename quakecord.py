import discord
from discord.ext import commands
import yaml
import asyncio
import websocket
import threading
import json
import asyncio
import logging
import json
import sys
import os
from datetime import datetime
from datetime import timedelta
import pytz
import pathlib
from sys import platform
from selenium.webdriver.chrome.options import Options
import folium
from selenium import webdriver
import time
import imgbbpy
import json
import os
import matplotlib.pyplot as plt

def save_json(typequake, magnitude, longitude, latitude, time, depth, region):
    earthquakes = []

    # Check if the JSON file exists and load it if it does
    if os.path.exists(getpath() + 'earthquakes.json'):
        with open(getpath() + 'earthquakes.json') as f:
            earthquakes = json.load(f)
    
    # Calculate the current time and the time one day ago
    now = datetime.now()
    one_day_ago = now - timedelta(days=1)
    print(one_day_ago)

    # Delete any entries older than one day
    earthquakes = [e for e in earthquakes if datetime.strptime(e['time'],"%Y-%m-%d %H:%M:%S") >= one_day_ago]

    # Create the earthquake data as a dictionary
    earthquake = {
        "type": typequake,
        "magnitude": magnitude,
        "longitude": longitude,
        "latitude": latitude,
        "time": time,
        "depth": depth,
        "region": region
    }

    # Add the new earthquake data to the list of earthquakes
    earthquakes.append(earthquake)

    # Write the list of earthquakes to the JSON file
    with open(getpath() + 'earthquakes.json', 'w') as f:
        json.dump(earthquakes, f, indent=4)

def uploadimage(imageloc,name):
    client = imgbbpy.SyncClient('imgbbpy_token')
    image = client.upload(file=imageloc,name=name)
    print(image.url)
    return(image.url)

def create_map(latitude, longitude, magnitude):
    m = folium.Map(location=[latitude, longitude], zoom_start=6, zoom_control=False,prefer_canvas=True)
    folium.CircleMarker(location=[latitude, longitude], radius=magnitude*5, color='red', fill=True, fill_color='red').add_to(m)
    return m

def create_map_history(listy):
    m = folium.Map(location=[0, 0], zoom_start=3, zoom_control=False,prefer_canvas=True)
    for location in listy: 
        folium.CircleMarker(location=[location['latitude'], location['longitude']], radius=float(location['magnitude'])*5, color='red', fill=True, fill_color='red').add_to(m)
    return m

def maptoimage(maploc):
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--headless')
    options.add_argument('--hide-scrollbars')
    options.add_argument("--start-maximized"); # open Browser in maximized mode
    options.add_argument("--no-sandbox"); # Bypass OS security model

    driver = webdriver.Chrome(options=options)
    driver.get("file://" + maploc)
    time.sleep(0.5)
    driver.save_screenshot(maploc.replace("html","png"))
    driver.close()

def getpath():
    path = ""
    path = pathlib.PureWindowsPath(str(os.path.dirname(os.path.realpath(__file__))))
    if(platform == "linux" or platform == "linux2"):
        path = str(path.as_posix()) + "/"
    else:
        path = str(path) + "\\"
    return path
intents = discord.Intents.default()
intents.message_content = True
activity = discord.Activity(type=discord.ActivityType.watching, name=" for earthquakes")
client = commands.Bot(command_prefix="%&", activity=activity, status=discord.Status.online, intents=intents, help_command=None)

def load_config():
    config = []
    try: 
        with open(getpath() + 'config.yml', 'r') as file: 
            config = yaml.load(file,Loader=yaml.Loader)
    except: 
        config = []
        save_config(config)
    return config

def checkperms(ctx):
    try:
        config = load_config()
        location = next((i for i, item in enumerate(config) if item["server"] == ctx.message.guild.id), None)
        if not (ctx.author.guild_permissions.administrator or
                any(role.id in config[location]['roles'] for role in ctx.author.roles)):
            return(False)
        else: 
            return(True)
    except TypeError: 
        config = load_config()
        config.append({"server":ctx.message.guild.id,"channel_id" : None,"mag_limit" : 0,"pausealerts":False,"disablemap":False,"roles":[]})
        save_config(config)
    except Exception as e:
        print("Error in CheckPerms " + str(e))
def save_config(config):
    with open(getpath() + 'config.yml', 'w') as file:
        yaml.safe_dump(config, file)

config = load_config()
selected_channel = None
def get_embed_color(magnitude):
    if magnitude < 2.5:
        return 0x00FF00  # Green
    elif magnitude < 4.5:
        return 0xFFFF00  # Yellow
    elif magnitude < 6:
        return 0xFFA500  # Orange
    else:
        return 0xFF0000  # Red
@client.event
async def on_ready():
    global selected_channel
    print(f'{client.user} has connected to Discord!')
    print(f'Connected to the following servers:')
    for guild in client.guilds:
        print(f'{guild.name} (id: {guild.id})')

@client.command()
async def test(ctx):
    await ctx.send("I am alive")

@client.command(name='setchannel', help='Sets the channel for earthquake notifications')
async def set_channel(ctx, channel: discord.TextChannel):
    if(checkperms(ctx) == False):
        await ctx.send("Oops! You do not have the required permissions to run this command.")
        return
    config = load_config()
    location = next((i for i, item in enumerate(config) if item["server"] == ctx.message.guild.id), None)
    if(location == None):
        config.append({"server":ctx.message.guild.id,"channel_id" : None,"mag_limit" : 0,"pausealerts":False,"disablemap":False,"roles":[]})
    else: 
        config[location]['channel_id'] = channel.id
    with open(getpath() + "config.yml", "w") as file:
        yaml.dump(config, file)
    await ctx.send(f'Earthquake notifications will now be sent to {channel.mention}')

@client.command(name='setroles', help='Adds a role to the allowed roles for running commands')
async def set_roles(ctx, *roles: discord.Role):
    if(checkperms(ctx) == False):
        await ctx.send("Oops! You do not have the required permissions to run this command.")
        return
    config = load_config()
    location = next((i for i, item in enumerate(config) if item["server"] == ctx.message.guild.id), None)
    
    allowed_roles = []
    for role in roles:
        allowed_roles.append(role.id)
    
    config[location]["roles"] = allowed_roles
    
    with open(getpath() + "config.yml", "w") as file:
        yaml.dump(config, file)
    
    await ctx.send(f'The following roles have been added to the allowed roles list: {", ".join([role.name for role in roles])}')


@client.command(name='help', help='Shows a list of available commands')
@commands.cooldown(1, 30, commands.BucketType.user)
async def help_command(ctx):
    if(checkperms(ctx) == False):
        await ctx.send("Oops! You do not have the required permissions to run this command.")
        return
    embed = discord.Embed(
        title='Available Commands',
        description='List of commands for Quakecord',
        color=0x3498DB
    )
    embed.add_field(name='%&status', value='Shows the status of the bot', inline=False)
    embed.add_field(name='%&ping', value='Pings the bot', inline=False)
    embed.add_field(name='%&setmaglimit', value='Sets the minimum magnitude for earthquake notifications', inline=False)
    embed.add_field(name='%&setchannel', value='Sets the channel for earthquake notifications', inline=False)
    embed.add_field(name='%&disablemap', value='Disable the map image from being sent', inline=False)
    embed.add_field(name='%&setroles', value='Set the roles that are able to access Quakecord', inline=False)
    embed.set_footer(text=f'Bot version: 1.0')

    await ctx.send(embed=embed)


@client.command(name='setmaglimit', help='Sets the magnitude limit for alerts')
async def set_channel(ctx, arg):
    if(checkperms(ctx) == False):
        await ctx.send("Oops! You do not have the required permissions to run this command.")
        return
    if(arg.isdigit() == True):
        config = load_config()
        location = next((i for i, item in enumerate(config) if item["server"] == ctx.message.guild.id), None)
        if(location == None):
            config.append({"server":ctx.message.guild.id,"channel_id" : None,"mag_limit" : 0,"pausealerts":False,"disablemap":False,"roles":[]})
        else: 
            config[location]["mag_limit"] = arg
        with open(getpath() + "config.yml", "w") as file:
            yaml.dump(config, file)
        await ctx.send(f'Magnitude post limit is now set to {str(arg)}')
    else: 
        await ctx.send(f'Error: You must specify a numeric value.')

@client.command(name='status', help='Shows the status of the bot settings')
async def status(ctx):
    try:
        if(checkperms(ctx) == False):
            await ctx.send("Oops! You do not have the required permissions to run this command.")
            return
        config = load_config()
        location = next((i for i, item in enumerate(config) if item["server"] == ctx.message.guild.id), None)
        channel = client.get_channel(config[location]['channel_id'])
        enabled = config[location]['pausealerts']
        enabledmap = config[location]['disablemap']
        limit = config[location]['mag_limit']
        roles = config[location]['roles']
        embed = discord.Embed(title="Quakecord Status for " + str(ctx.message.guild.name), color=0x3498DB)
        embed.add_field(name="Alerts Paused:", value="✅" if enabled else "❌", inline=True)
        embed.add_field(name="Map Disabled:", value="✅" if enabledmap else "❌", inline=True)
        try:
            embed.add_field(name="Notification Channel:", value=channel.mention, inline=True)
        except AttributeError: 
            embed.add_field(name="Notification Channel:", value="Not setup", inline=True)
        embed.add_field(name="Magnitude Limit:", value=limit, inline=True)
        embed.add_field(name="Allowed roles:", value=', '.join(map(str, roles)), inline=True)
        await ctx.send(embed=embed)
    except Exception as e:
        print(e)
@client.command(name='pause', help='Sets the magnitude limit for alerts')
async def pause(ctx):
    if(checkperms(ctx) == False):
        await ctx.send("Oops! You do not have the required permissions to run this command.")
        return
    config = load_config()
    location = next((i for i, item in enumerate(config) if item["server"] == ctx.message.guild.id), None)
    if(location == None):
        config.append({"server":ctx.message.guild.id,"channel_id" : None,"mag_limit" : 0,"pausealerts":False,"disablemap":False,"roles":[]})
    else: 
        config[location]['pausealerts'] = not config[location]['pausealerts']
    with open(getpath() + "config.yml", "w") as file:
        yaml.dump(config, file)
    if(config[location]['pausealerts'] == True): 
        action = "paused"
    else: 
        action = "unpaused"
    await ctx.send(f'Alerts currently {str(action)}')

@client.command(name='tips', help='Displays tips for what to do during an earthquake')
@commands.cooldown(1, 30, commands.BucketType.user)
async def tips(ctx):
    if(checkperms(ctx) == False):
        await ctx.send("Oops! You do not have the required permissions to run this command.")
        return
    embed = discord.Embed(title="What to do if you are in...", color=0x3498DB)

    # Category 1: A car
    embed.add_field(name="🚗 A car", value="If you are in a car during an earthquake, pull over to the side of the road and stop. Avoid stopping under bridges, overpasses, and power lines. Stay inside the car until the shaking stops.", inline=False)

    # Category 2: A highrise
    embed.add_field(name="🏢 A highrise", value="If you are in a highrise building during an earthquake, stay calm and stay where you are. Avoid running outside or to other rooms during shaking. If you are near a desk or table, duck under it for protection.", inline=False)

    # Category 3: A house
    embed.add_field(name="🏠 A house", value="If you are in a house during an earthquake, drop to the ground, take cover under a sturdy table or desk, and hold on to it. If there is no table or desk nearby, sit against an interior wall and protect your head and neck with your arms.", inline=False)

    # Category 4: Outside
    embed.add_field(name="🌲 Outside", value="If you are outside during an earthquake, move away from buildings, power lines, and other structures. Stay in the open, away from trees, signs, buildings, and other structures that could fall.", inline=False)

    # Category 5: At the beach
    embed.add_field(name="🏖️ At the beach", value="If you are at the beach during an earthquake, move inland away from the water and any tall structures. If a tsunami is generated, it could reach the shore within minutes.", inline=False)

    await ctx.send(embed=embed)


@client.command(name='disablemap', help='Disable the map from being shown on new alerts')
async def disablemap(ctx):
    if(checkperms(ctx) == False):
        await ctx.send("Oops! You do not have the required permissions to run this command.")
        return
    config = load_config()
    location = next((i for i, item in enumerate(config) if item["server"] == ctx.message.guild.id), None)
    if(location == None):
        config.append({"server":ctx.message.guild.id,"channel_id" : None,"mag_limit" : 0,"pausealerts":False,"disablemap":False,"roles":[]})
    else: 
        config[location]['disablemap'] = not config[location]['disablemap']
    with open(getpath() + "config.yml", "w") as file:
        yaml.dump(config, file)
    if(config[location]['disablemap'] == True): 
        action = "disabled"
    else: 
        action = "enabled"
    await ctx.send(f'Map sending is currently {str(action)}')

@client.command(name='ping', help='Pings the bot')
async def ping(ctx):
    try:
        if(checkperms(ctx) == False):
            await ctx.send("Oops! You do not have the required permissions to run this command.")
            return
        start = time.perf_counter()
        async with ctx.typing():
            end = time.perf_counter()
        embed = discord.Embed(title='🏓 Pong!', description=f'Response time: {(end - start) * 1000:.2f}ms')
        await ctx.send(embed=embed)
    except Exception as e:
        print("Ping error: " + str(e))
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Sorry, I don't recognize that command. Use the **%&help** command to see available commands.")

def parse_time(time_string):
    try:
        hours = int(time_string)
    except ValueError:
        return None
    
    if hours > 24:
        return 24
    
    return hours

@client.command(name='history', help='Allows you to see the last X hours of earthquakes.')
@commands.cooldown(1, 30, commands.BucketType.user)
async def history(ctx, hours: str):
    try:
        if(checkperms(ctx) == False):
            await ctx.send("Oops! You do not have the required permissions to run this command.")
            return
        try:
            hours = parse_time(hours)
            if hours is None:
                await ctx.send("Please specify a numeric value for hours (e.g. 5 or 6).")
                return
            
            if hours > 24:
                await ctx.send("Unfortunately, we do not store data past 24 hours. So here is the last 24 only.")
                hours = 24
            
            # load the earthquakes data from the file
            with open(getpath() + "earthquakes.json", "r") as f:
                data = json.load(f)
            
            # filter the earthquakes that occurred in the specified time range
            now = datetime.now()
            time_range = now - timedelta(hours=hours)
            print(time_range)
            earthquakes = [e for e in data if datetime.strptime(e['time'],'%Y-%m-%d %H:%M:%S') >= time_range]
            
            # create the embed with the earthquakes information
            embed = discord.Embed(title=f"Earthquakes in the last {hours} hours", color=0x008080)
            times = []
            magnitudes = []

            async with ctx.typing():
                #m = create_map_history(earthquakes)
                #m.save(getpath() + r"historical_map.html")
                #maptoimage(getpath() + r"historical_map.html")
                #imageurl = uploadimage(getpath() + "historical_map.png","Historical_map")
                #if(earthquakes != []):
                #    embed = embed.set_image(url = str(imageurl))
                for e in earthquakes:
                    embed.add_field(
                        name=f"{e['region']} ({e['magnitude']} magnitude)",
                        value=f"Time: {e['time']}\nDepth: {e['depth']} km\nEpicenter: {e['latitude']},{e['longitude']}",
                        inline=False
                    )
                    times.append(e['time'])
                    magnitudes.append(e['magnitude'])
                if(earthquakes == []):
                    embed.add_field(name="",value="N/A")
                # if(times != [] and magnitudes != []):
                #     plt.plot(times,magnitudes,"o")
                #     plt.xlabel("Time")
                #     plt.ylabel("Magnitude")
                #     plt.title("Earthquakes in the world in the last " + str(hours) + " hours")
                #     plt.grid(True)
                #     plt.savefig(getpath() + "plt.png")
                await ctx.send(embed=embed)
        except Exception as e: 
            print("Error with Earthquakes: " + str(e))
    except Exception as e: 
        print(e)

@client.event
async def on_earthquake(typequake, magnitude, longitude, latitude, time, depth, region):
    print("Quake")
    try:
        color = get_embed_color(float(magnitude))
        timedatetime = datetime.strptime(time,("%Y-%m-%d %H:%M:%S"))
        if(typequake == "update"):
            title = "Earthquake Update"
        else: 
            title = "Earthquake Alert"
        map = create_map(float(latitude), float(longitude), float(magnitude))
        map.save(getpath() + r"map.html")
        maptoimage(getpath() + r"map.html")
        embed = discord.Embed(title=title,
                            description=f'Magnitude: {str(magnitude)}\n'
                                        f'Location: {str(longitude)}, {str(latitude)}\n'
                                        f'Region: {str(region)}\n'
                                        f'Time: {str(time)} UTC\n'
                                        f'Depth: {str(depth)} km\n',
                            url=f"http://www.google.com/maps/place/{latitude},{longitude}",
                            color=color)
        config = load_config()
        if(typequake != "update"):
            save_json(typequake, magnitude, longitude, latitude, time, depth, region)
        for x in config:
            print(x)
            if(((float(magnitude) >= float(x['mag_limit'])) and typequake != "update") and x['pausealerts'] == False):
                imageurl = uploadimage(getpath() + "map.png",region + str(magnitude) + str(depth))
                if(x['disablemap'] == False):
                    embed = embed.set_image(url = str(imageurl))
                if(x['channel_id'] != None):
                    channel = client.get_channel(int(x['channel_id']))
                    await channel.send(embed=embed)
            else:
                True
    except Exception as e:
        print(e)

def on_message_ws(ws, message):
    datas = json.loads(message)
    data = datas['data']['properties']
    magnitude = str(data['mag'])
    longitude = data["lon"]
    latitude = data["lat"]
    time = datetime.strptime(data['time'],'%Y-%m-%dT%H:%M:%S.%fZ')
    time_utc = pytz.utc.localize(time)
    time = str(time_utc.strftime("%Y-%m-%d %H:%M:%S"))
    depth = str(data["depth"])
    region = str(data['flynn_region'])
    quaketype = datas['action']
    asyncio.run_coroutine_threadsafe(on_earthquake(quaketype, magnitude, longitude, latitude, time, depth, region), client.loop)


def on_error_ws(ws, error):
    print(f'WebSocket error: {error}')

def on_close_ws(ws):
    print('WebSocket closed.')

def run_websocket():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://www.seismicportal.eu/standing_order/websocket", on_message=on_message_ws)
    ws.run_forever()



if __name__ == "__main__":
    wst = threading.Thread(target=run_websocket)
    wst.start()

    client.run('YOUR_TOKEN')
