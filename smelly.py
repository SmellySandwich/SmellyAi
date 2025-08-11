# Discord and other imports.
import discord
from discord.ext import commands, tasks
from discord import File

# Standard imports.
import sqlite3
import os
from time import sleep
from datetime import datetime

# AI imports.
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import pyttsx3

# Custom imports.
from lib.env.settings import DISCORD_API_TOKEN
from lib.sqlite3.database import SmellyMemory
from lib.genai.smellychat import SmellyAI
from lib.genai.genimage import Image_Gen

# Create instances.
memory = SmellyMemory()
smellyai = SmellyAI()
image_gen = Image_Gen()


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=discord.Intents.default())

    # Bot forced commands with !
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
        
        if message.author.name != 'SmellyAiBeta': # Prevents SmellyBot from answering himself in a loop.

            ctx = await bot.get_context(message)
            content = ctx.message.content # Pull the message string from content.
            name = message.author.global_name
            
            if content.lower() != '!smellybot': # Handles error if channel is not yet being watched.

                try:
                    memory.update_memory(channel, name, content)

                    if ('smellybot' or 'smellybot?' or 'smellybot,' or 'smellybot!') in content.lower():
                        
                        response = smellyai.chatbot(channel, content)
                        



                        ''' Execute functions based on specific return '''

                        # Image generation.
                        if response[:2] == '01':
                            generate = image_gen.generate(channel, response)

                            if generate == 'Sorry pictures are done for today.':
                                await message.reply(generate)

                            elif generate == "Sorry I can't process this picture.":
                                await message.reply(generate)

                            else:
                                await message.channel.send(file=File(f'{str(channel)}.png'))
                                os.remove(f'{str(channel)}.png')


                        # Voice file output.
                        if response[:2] == '02':
                            engine = pyttsx3.init()
                            engine.setProperty('rate', 150)

                            engine.save_to_file(f"{response[3:]}", f'{str(channel)}.mp3')
                            engine.runAndWait()
                            engine = pyttsx3.init()
                            
                            await message.channel.send(file=File(f'{str(channel)}.mp3'))
                            os.remove(f'{str(channel)}.mp3')




                        # Respond to input if no special functions are called.
                        else:
                            await message.reply(response)

                except sqlite3.OperationalError:
                    pass

        # Allow bot commands to be called while using on_message.   
        await bot.process_commands(message)
  
    # RUN SMELLY, RUN!
    bot.run(DISCORD_API_TOKEN)

run()