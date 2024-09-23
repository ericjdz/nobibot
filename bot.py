import asyncio
import discord
import random
import aiohttp
import csv
from dotenv import load_dotenv
load_dotenv()
import requests
from discord.ext import commands, tasks
import time
import os
import google.generativeai as genai


TOKEN = os.getenv('TOKEN')

# Intents
intents = discord.Intents.default()
intents.message_content = True  

# Store the start time of the bot
start_time = time.time()



genai.configure(api_key=os.getenv('GENAPI'))

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(model_name="tunedModels/nobi-bot-sk54degtx8qr", generation_config=generation_config)




# Bot prefix
bot = commands.Bot(command_prefix='?', intents=intents)


# Function to load messages from CSV
def load_messages_from_csv(filepath):
    messages = []
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:  # Check if the row is not empty
                messages.append(row[0])
    return messages



# List of random poems
random_poems = load_messages_from_csv('message_csv\\random_poems.csv')

# List of possible responses when the bot is mentioned
mention_responses = load_messages_from_csv('message_csv\\mention_responses.csv')

wordsper20 = load_messages_from_csv('message_csv\\messages.csv')


# # Background task to send a message every 5 minutes
# @tasks.loop(minutes=30.0)
# async def send_periodic_message():
#     channel = bot.get_channel(os.getenv('Channel_ID'))  # Replace with your channel ID
#     if channel:
#         user = channel.guild.get_member(os.getenv('member_ID'))  # Replace with the user ID you want to mention
#         message = random.choice(wordsper20)
#         if user:
#             message = f"{message.replace('{user}', user.mention)}"
#         await channel.send(message)
#     else:
#         print("Channel not found")
@bot.event
async def on_message(message):
    # Check if the bot is mentioned in the message
    if bot.user in message.mentions:
        #if there is no message after or before the mention, return a random response
        if message.content == f'<@!{bot.user.id}>' or message.content == f'<@{bot.user.id}>':
            response = random.choice(mention_responses)
            await message.channel.send(f"{response} {message.author.mention}")
        else:
            # create a prompt with the message
            Mcontent = message.content.replace(f'<@!{bot.user.id}>', '@NobiBot').replace(f'<@{bot.user.id}>', '@NobiBot')
            print(Mcontent)
            prompt = f'{message.author.display_name}: {Mcontent}'
            print(f'\n\nNEW PROMPT\n{prompt}')
            try:
                response = model.generate_content(f'You are an arrogant discord bot named NobiBot. Respond to this message of this user as an arrogant discord bot, but still provide the answer.\n{prompt}')
                if response.text == "":
                    response = model.generate_content(f'You are an arrogant discord bot named NobiBot. Respond to this message of this user as an arrogant discord bot, but still provide the answer.\n{prompt}')
                await message.channel.send(response.text)
            except Exception as e:
                print(f'An error occurred: {e}')
                await message.channel.send(f'Can you repeat that?')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
#    send_periodic_message.start()

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command(name='love')
async def love(ctx, *args):
    if len(args) < 2:
        await ctx.send("Please provide at least one mention and a message.")
        return

    if len(args) == 2:
        # One mention and a message
        mention = args[0]
        message = args[1]
        await ctx.send(f"{mention} loves {message}")

    elif len(args) == 3:
        # Two mentions and a message
        mention1 = args[0]
        mention2 = args[1]
        message = args[2]
        await ctx.send(f"{mention1} and {mention2} love {message}")

    else:
        await ctx.send("Too many arguments. Use either one mention or two mentions and a message.")

@bot.command(name='random')
async def random_command(ctx, *args):
    # Select a random message from the list
    response = random.choice(random_poems)
    # Send the message
    await ctx.send(response)

@bot.command(name='dogimg')
async def random_dog(ctx):
    """Fetches a random dog image."""
    try:
        response = requests.get('https://dog.ceo/api/breeds/image/random')
        response.raise_for_status()
        dog_data = response.json()
        dog_image_url = dog_data['message']

        embed = discord.Embed(title='Random Dog', color=discord.Color.orange())
        embed.set_image(url=dog_image_url)

        await ctx.send(embed=embed)
    except requests.exceptions.RequestException as e:
        await ctx.send(f'An error occurred: {e}')


@bot.command(name='catimg')
async def random_cat(ctx):
    """Fetches a random cat image."""
    try:
        response = requests.get('https://api.thecatapi.com/v1/images/search')
        response.raise_for_status()
        cat_data = response.json()[0]
        cat_image_url = cat_data['url']

        embed = discord.Embed(title='Random Cat', color=discord.Color.purple())
        embed.set_image(url=cat_image_url)

        await ctx.send(embed=embed)
    except requests.exceptions.RequestException as e:
        await ctx.send(f'An error occurred: {e}')

@bot.command(name='8ball')
async def eight_ball(ctx, *, question: str):
    responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes, definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."
    ]
    await ctx.send(f'{random.choice(responses)}')


@bot.command(name='catfact')    
async def cat_fact(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://catfact.ninja/fact') as response:
            if response.status != 200:
                await ctx.send('Could not fetch cat fact.')
                return
            data = await response.json()
            await ctx.send(data['fact'])

@bot.command(name='dogfact')
async def dog_fact(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://dog-api.kinduff.com/api/facts') as response:
            if response.status != 200:
                await ctx.send('Could not fetch dog fact.')
                return
            data = await response.json()
            await ctx.send(data['facts'][0])

@bot.command(name='say')
async def say(ctx, *, message: str):
    await ctx.send(message)

@bot.command(name='announce')
async def announce(ctx, channel: discord.TextChannel, *, message: str):
    await channel.send(message)


@bot.command(name='say2')
async def say2(ctx, *, message: str):
    await ctx.send(message)  # Send the user's message
    await ctx.message.delete()  # Delete the original command message

@bot.command(name='joke')
async def random_joke(ctx):
    """Fetches a random joke."""
    try:
        response = requests.get('https://v2.jokeapi.dev/joke/Any')
        response.raise_for_status()
        joke_data = response.json()
        if joke_data['type'] == 'single':
            joke = joke_data['joke']
        else:
            joke = f"{joke_data['setup']} - {joke_data['delivery']}"

        await ctx.send(joke)
    except requests.exceptions.RequestException as e:
        await ctx.send(f'An error occurred: {e}')


# command that takes a message as an argument and counts the number of characters
@bot.command(name='count')
async def count(ctx, *, message: str):
    # count the number of characters in the message
    num_chars = len(message)
    await ctx.send(f"The message '{message}' has {num_chars} characters.")

@bot.command(name='ping')
async def ping(ctx):
    """Responds with 'Pong!' and the bot's latency."""
    latency = round(bot.latency * 1000)  # Convert latency to milliseconds
    await ctx.send(f'Pong! Latency: {latency}ms')

@bot.command(name='uptime')
async def uptime(ctx):
    """Shows how long the bot has been running."""
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    uptime_str = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))
    await ctx.send(f'Uptime: {uptime_str}')

#roll with a specified number of sides
@bot.hybrid_command(name='roll')
async def roll(ctx, sides: int = 100):
    """Rolls a random number between 1 and the specified number of sides (default is 100)."""
    if sides < 2:
        await ctx.send('The number of sides must be at least 2.')
        return
    number = random.randint(1, sides)
    await ctx.send(f'You rolled a {number}!')


from bs4 import BeautifulSoup

@bot.command(name='scrape')
async def scrape(ctx, url: str):
    """Scrapes the HTML content of the specified URL and sends it as a file."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        prettified_html = soup.prettify()

        # Save the prettified HTML to a file
        file_path = 'scraped_page.html'
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(prettified_html)

        # Send the file to the Discord channel
        await ctx.send(file=discord.File(file_path))

        # Optionally, delete the file after sending it
        os.remove(file_path)
    except requests.exceptions.RequestException as e:
        await ctx.send(f'An error occurred: {e}')

# command that takes a user as an argument and displays their avatar
@bot.command(name='avatar')
async def avatar(ctx, user: discord.User = None):
    """Displays the avatar of the specified user or the message author if no user is specified."""
    if user is None:
        user = ctx.author
    await ctx.send(user.display_avatar.url)

import json
# Define your Custom Search Engine ID and API Key
CSE_ID = os.getenv('CSE')
API_KEY = os.getenv('API_KEY')

# Function to search Pinterest and fetch images
async def search_pinterest(query):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": CSE_ID,
        "key": API_KEY,
        "searchType": "image",
        "siteSearch": "pinterest.com",  # Search specifically on Pinterest
        "num": 10  # Get 10 results
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(search_url, params=params) as response:
            data = await response.json()
            if 'items' in data:
                images = [item['link'] for item in data['items']]
                return images
            else:
                return []

# Command to perform Pinterest search and display images with reaction navigation
@bot.command(name='pinterest')
async def pinterest_search(ctx, *, query):
    images = await search_pinterest(query)
    if images:
        current_index = 0  # Track the current image index
        embed = discord.Embed(title=f"Search results for: {query}", color=discord.Color.blue())
        embed.set_image(url=images[current_index])
        message = await ctx.send(embed=embed)
        
        # Add the right arrow reaction to the message
        await message.add_reaction('➡️')

        # Function to handle reaction for next image
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '➡️' and reaction.message.id == message.id

        # Infinite loop to handle reaction events (for a limited time or until canceled)
        while True:
            try:
                # Wait for the reaction to be added by the user
                reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

                if str(reaction.emoji) == '➡️':
                    # Move to the next image
                    current_index += 1
                    if current_index >= len(images):
                        current_index = 0  # Loop back to the first image if at the end

                    # Update the embed with the new image
                    embed.set_image(url=images[current_index])
                    await message.edit(embed=embed)
                    
                    # Remove the user's reaction to allow them to press it again
                    await message.remove_reaction('➡️', user)

            except asyncio.TimeoutError:
                # If the user does not react within 60 seconds, exit the loop
                break
    else:
        await ctx.send("No results found.")
 
 

@bot.command(name='generate')
async def generate_text(ctx, *, prompt: str):
    """Generates text using the specified prompt."""
    try:
        response = model.generate_content(prompt)
        await ctx.send(response.text)
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')

@bot.command(name='readchat')
async def generate_response(ctx):
    channel = ctx.channel
    messages = []
    async for message in channel.history(limit=20):
        messages.insert(0, f"{message.author.display_name}: {message.content}")
    
    messages.pop(len(messages) - 1)
    prompt = "\n".join(messages)
    
    try:
        print(f'\n\nNEW PROMPT\n{prompt}')
        response = model.generate_content(f'You are an arrogant discord bot on a discord server, you read chat logs on a discord server and make comments about the chat logs. The following are chat logs of the discord server you are in. Respond by judging the users in the server according to their messages, make jokes or comments, or even react to their messages. You can also mention a specific user about a message they sent. \n{prompt}')
        await ctx.send(response.text)
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')

        
# Run the bot
bot.run(TOKEN)
