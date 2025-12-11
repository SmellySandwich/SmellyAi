# Discord imports.
import discord
from discord.ext import commands, tasks
from discord import File

# Standard imports.
import os
import time
import random
import requests
from io import BytesIO
from datetime import datetime, timezone
import sqlite3

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

client = discord.Client(intents=discord.Intents.default())

def run():
    intents = discord.Intents.default()
    intents.message_content = True
    # client = discord.Client(intents=discord.Intents.default())

    bot = discord.ext.commands.Bot(command_prefix='!', intents=intents, case_insensitive=False, help_command=None)
    bot.version = 'lite'

    @bot.event
    async def on_ready():
        print('Smelly is watching...')
        reminders.start()


    @bot.command()
    async def smellybot(ctx):
        """ SmellyBot's call command to begin watching a channel. Call database and create a row for the channel. 
        """

        channel = ctx.channel.id
        output = memory.activate(channel)

        await ctx.send(output)


    @tasks.loop(minutes=1)
    async def reminders():
        """ Check reminders.txt every minute for scheduled reminders.
        """

        with open('memory_bank/reminders.txt', 'r', encoding='utf-8') as file:
            reminders = file.read()
            
            utc_time = datetime.now(timezone.utc)
            formatted_utc_time = (utc_time.strftime("%Y-%m-%d %H:%M").replace(':', '')).split()
            current_date = formatted_utc_time[0]
            current_time = formatted_utc_time[1]
            
            try:
                list_split = reminders.split('\n')
                for i in list_split:
                    reminder = i.split()

                    user_id = reminder[0]
                    channel = reminder[1]
                    reminder_date = reminder[2]
                    reminder_time = reminder[3].replace(':', '')
                    message = ' '.join(reminder[4:])

                    if current_date == reminder_date:
                        if current_time == reminder_time:
                    
                            channel = bot.get_channel(int(channel))
                            await channel.send(f"<@{user_id}> {message}")

            except:
                pass

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
        version = 'heavy'
        
        if message.author.name != 'SmellyAi': # Prevents SmellyBot from answering himself in a loop.

            ctx = await bot.get_context(message)
            content = ctx.message.content # Pull the message string from content.
            name = message.author.global_name
            
            if content.lower() != '!smellybot': # Handles error if channel is not yet being watched.

                if content.lower() == 'clear':
                    conn = sqlite3.connect('memory_bank/channel_memory.db')
                    c = conn.cursor()
                    c.execute("UPDATE Memory SET chat_memory = ? WHERE channel = ?", ("", channel))
                    conn.commit()
                    conn.close()
                    return
                
                if content.lower() == 'forget':
                    conn = sqlite3.connect('memory_bank/channel_memory.db')
                    c = conn.cursor()
                    c.execute("UPDATE Memory SET personal_memory = ? WHERE channel = ?", ("", channel))
                    conn.commit()
                    conn.close()
                    return
                
                if content.lower() == 'lite': bot.version = 'lite'
                elif content.lower() == 'heavy': bot.version = 'heavy'
                
                try:

                    # Send .txt for for input     
                    if message.attachments:
                        for attachment in message.attachments:
                            if attachment.filename.lower().endswith('.txt'):
                                file_content = await attachment.read()
                                content = file_content.decode('utf-8')
                                response = memory.update_chat_memory(channel, user, name, content)

                    # If the sent message is an image use OCR to populate database with the description. 
                        for attachment in message.attachments:
                            request = requests.get(attachment.url)
                            img = Image.open(BytesIO(request.content))
                            
                            client = genai.Client(api_key=GEMINI_API_KEY)
                            response = client.models.generate_content(
                            model="gemini-2.5-flash", contents=['Explain, emphasizing important detials, what you see in this picture.', img]
                            )
                            # explain what you see in this picture in 100 words or less please only give important information.'
                            content = f"This is a picture - {response.text}"
                                
                    try:
                        memory.update_chat_memory(channel, user, name, content) # Send user message to memory string.       
                    except IndexError as e:
                        pass

                    # Add data to game database.
                    if 'smellyadd' in content.lower():
                        if channel == 1170014109438316615 or channel == 1209129630255022131 or channel == 1407181532174487562:
                            data = await smellyai.chatbot(channel, f'{content}')

                            response = mod.save_game_data(name, data)
                            await message.reply(response)

                    # Retrieve data from game database.
                    if 'smellymod' in content.lower():
                        if channel == 1170014109438316615 or channel == 1290642325420118019 or channel == 1209129630255022131 or channel == 1407181532174487562:
                            query = await smellyai.chatbot(channel, f'{content}')
                            response = mod.return_game_data(channel, query)
                            await message.reply(response)

                    # Personal memory for ordinary channels.
                    if 'smellybot remember' in content.lower():
                        response = memory.update_personal_memory(channel, user, name, content)
                        await message.reply(response)

                    # Standard SmellyBot calls - not mod related.
                    elif ('smellybot' or 'smellybot?' or 'smellybot,' or 'smellybot!') in content.lower():
                        
                        response = await smellyai.chatbot(channel, content, bot.version)

                        


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

                            file_name = random.randint(1, 100000)
                            engine.save_to_file(f"{response[3:]}", f'{str(file_name)}.mp3')
                            engine.runAndWait()
                            engine = pyttsx3.init()
                            
                            await message.channel.send(file=File(f'{str(file_name)}.mp3'))
                            os.remove(f'{str(file_name)}.mp3')

                        # Create reminder.
                        elif response[:2] == '03':
                            response_split = response.split()
                            
                            
                            reminder_time = f"{response_split[1]} {response_split[2]}"
                            reminder = ' '.join(response_split[3:])
                            
                            with open('memory_bank/reminders.txt', 'a', encoding='utf-8') as file:
                                file.write(f'{user} {channel} {reminder_time} {reminder}\n')

                            await message.reply(f"Done! I'll send you a reminder.")

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
