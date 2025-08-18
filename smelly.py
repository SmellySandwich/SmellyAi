# Discord imports.
import discord
from discord.ext import commands, tasks
from discord import File

# Standard imports.
import sqlite3
import os
from time import sleep
from datetime import datetime
import requests
from io import BytesIO

# AI imports.
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import pyttsx3 # Bot voice.

# Custom imports.
from lib.env.settings import DISCORD_API_TOKEN, GEMINI_API_KEY
from lib.sqlite3.database import SmellyMemory
from lib.genai.smellychat import SmellyAI
from lib.genai.genimage import Image_Gen
from lib.mod.mod_command import Mod

# Create instances.
memory = SmellyMemory()
smellyai = SmellyAI()
image_gen = Image_Gen()
mod = Mod()

local_converstaion_memory = []

client = discord.Client(intents=discord.Intents.default())
def run():
    intents = discord.Intents.default()
    intents.message_content = True
    # client = discord.Client(intents=discord.Intents.default())

    # Bot enables with $smellybot
    bot = discord.ext.commands.Bot(command_prefix='!', intents=intents, case_insensitive=False, help_command=None)

    @bot.event
    async def on_ready():
        print('Smelly is watching...')


    @bot.command()
    async def smellybot(ctx):
        """ SmellyBot's call command to begin watching a channel. Call database and create a row for the channel. 
        """

        channel = ctx.channel.id
        output = memory.activate(channel)

        await ctx.send(output)


    @bot.event
    async def on_message(message):

        """ Smelly will read each channel message in real time. When smelly is called in a channel (!smellybot)
            a row for that channel will be created in his memory database. The database will contain a large
            string of the entire message history for each channel.

            As messages are sent the bot will perform certain tasks:

            1) If the word contains the string 'smellybot' in it smelly will iterate through the entire
               channel history and answer the inquiry accordingly.

            2) SmellyBot will append the channels database string with the new message.
               username: [global discord name] message: [message to record]

            3) SmellyBot will have a variety of triggers that will return a function call
               within discord. This will include reminders, games, custom pictures, etc.
        """

        channel = message.channel.id
        user = message.author.id
        
        if message.author.name != 'SmellyAiBeta': # Prevents SmellyBot from answering himself in a loop.

            ctx = await bot.get_context(message)
            content = ctx.message.content # Pull the message string from content.
            name = message.author.global_name
            
            if content.lower() != '!smellybot': # Handles error if channel is not yet being watched.

                try:

                    # Forced commands for smellybot.

                    # If the sent message is an image use OCR to populate database with the description.
                    if message.attachments:
                        for attachment in message.attachments:
                            request = requests.get(attachment.url)
                            img = Image.open(BytesIO(request.content))
                            
                            client = genai.Client(api_key=GEMINI_API_KEY)
                            response = client.models.generate_content(
                            model="gemini-2.5-flash", contents=['explain what you see in this picture in detail. Ensure all text is processed neatly and translated to english.', img]
                            )
                            
                            content = f"This is a picture - {response.text}"
                    
                    try:
                        memory.update_chat_memory(channel, user, name, content) # Send user message to memory string.       
                    except IndexError as e:
                        print(f'Error in smelly.py line 107: {e}')

                    # Add data to game database.
                    if 'smellyadd' in content.lower():
                        if channel == 1170014109438316615 or channel == 1396633305285267592:
                            data = await smellyai.chatbot(channel, f'{content}')

                            response = mod.save_game_data(name, data)
                            await message.reply(response)

                    # Retrieve data from game database.
                    if 'smellymod' in content.lower():
                        if channel == 1170014109438316615 or channel == 1396633305285267592:
                            query = await smellyai.chatbot(channel, f'{content}')
                            response = mod.return_game_data(query)

                            await message.reply(response)
                            

                    # Standard SmellyBot calls - not mod related.
                    elif ('smellybot' or 'smellybot?' or 'smellybot,' or 'smellybot!') in content.lower():
                        
                        # await message.reply('Sorry folks, I will be down for a few hours. Feel free to contact customer serv... never mind, lost cause. BE BACK SOON!')
                        # return

                        response = await smellyai.chatbot(channel, content)

                        



                        ''' Execute functions based on specific return '''

                        # Image generation.
                        if response[:2] == '01':
                            generate = await image_gen.generate(channel, response)
                            
                            if generate == "Sorry I can't process this picture.":
                                await message.reply(generate)

                            else:
                                await message.channel.send(file=File(f'{str(generate)}.png'))
                                os.remove(f'{str(generate)}.png')

                        # Voice file output.
                        elif response[:2] == '02':
                            engine = pyttsx3.init()
                            engine.setProperty('rate', 150)

                            engine.save_to_file(f"{response[3:100]}", f'{str(channel)}.mp3')
                            engine.runAndWait()
                            engine = pyttsx3.init()
                            
                            file_remove =  await message.channel.send(file=File(f'{str(channel)}.mp3'))
                            os.remove(f'{str(file_remove)}.mp3')


                        # Respond to input if no special functions are called.
                        else:
                            await message.reply(response)


                except Exception as e:
                    print(f'Error in smelly.py: {e}\n')
                    pass

        # Allow bot commands to be called while using on_message.   
        await bot.process_commands(message)
  
    # RUN SMELLY, RUN!
    bot.run(DISCORD_API_TOKEN)

run()
