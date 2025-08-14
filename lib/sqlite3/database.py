# Standard imports.
import sqlite3

# Clean-up text imports.
import emoji   
import re

# AI imports.
from google import genai

# Custom imports.
from lib.env.settings import GEMINI_API_KEY


class SmellyMemory:

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        
    def activate(self, channel:int): 
            """ Activate SmellyBot for channel. Database will be created for his memory.
            """   

            if channel == 1170014109438316615:
                 conn = sqlite3.connect('memory_bank/mod_memory.db')
            else:
                conn = sqlite3.connect('memory_bank/channel_memory.db')
            c = conn.cursor()

            # Check to see if channel exists.
            c.execute("SELECT memory FROM Memory WHERE channel = ?", (channel,))
            channel_exists = c.fetchall()
            
            if channel_exists: return ('I am already listening.')
            
            else:            
                c.execute("INSERT INTO Memory (channel) VALUES (?)", (channel,))
                conn.commit()
                conn.close()
                
                return f'''Hey there! It's me... SmellyBot! I will get in on the conversation when i hear smellybot.\n
Shhhhh... it's ok now guys. SmellyBot is here.
                '''
            

    def update_memory(self, channel:int, name:str, content:str):
            """ Add the new message to the existing 'memory string'.
            """

            if channel == 1170014109438316615:
                 conn = sqlite3.connect('memory_bank/mod_memory.db')
            else:
                conn = sqlite3.connect('memory_bank/channel_memory.db')
            c = conn.cursor()        

            c.execute("SELECT memory FROM Memory WHERE channel = ?", (channel,))
            smelly_memory = c.fetchall()[0][0]
            smelly_first_output = 'SmellyBot:Greetings! I am SmellyBot, ready to assist with your questions and tasks. How may I help you today in this channel?'        

            # After Smellybot is called insert first entry to database.
            if smelly_memory is None:
                c.execute("UPDATE Memory SET memory = ? WHERE channel = ?", (f'{smelly_first_output}-{name}:{content}-', channel))
                conn.commit()
                conn.close()

            # If there is a memory, pull the entire string and append the new content.              
            else:
                c.execute("SELECT memory FROM Memory WHERE channel = ?", (channel,))
                memory_string = c.fetchall()[0][0]
                new_memory_string = f'{memory_string}{name}:{content}-'

                c.execute("UPDATE Memory SET memory = ? WHERE channel = ?", (new_memory_string, channel))
                conn.commit()
                conn.close()


    def image_input_to_game_memory(self, user:int, response:str):
        """ Image data to be interpreted and stored in game memory.
        """

        # if channel == 1170014109438316615:
        if user == 335439606793109504 or user == 1165085792843092040:
            conn = sqlite3.connect('memory_bank/game_memory.db')        
            c = conn.cursor()

            c.execute("SELECT memory FROM Memory")
            memory_string =  c.fetchall()[0][0]
            new_memory = f"{memory_string}\n\n{response}"

            c.execute("UPDATE Memory SET memory = ? WHERE reference = ?", (new_memory, 1))
            conn.commit()
            conn.close()


    def update_game_memory(self, user:int, response:str):
        """ Update mod specified information to game memory.
        """
    
        if user == 335439606793109504 or user == 1165085792843092040:
            conn = sqlite3.connect('memory_bank/game_memory.db')        
            c = conn.cursor()
        
            c.execute("SELECT memory FROM Memory")
            memory_string =  c.fetchall()[0][0]
            response = response[2:]
            new_memory = f"{memory_string}\n\nUPDATE IN CURRENT DATA:{response}"

            c.execute("UPDATE Memory SET memory = ? WHERE reference = ?", (new_memory, 1))
            conn.commit()
            conn.close()

            fun_comment = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=f"Say something funny about updating data."
                )

            return f'OK! My game memory has been updated:\n\n{response}\n\n{fun_comment.text}'


    def cleanup(self):
        """ Cleans up the data copied to the th_data.txt. This will remove emojis and < anything written here >
            from data and return 'All clean!'.
        """

        # with open("memory_bank/th_data.txt", "r", encoding='utf-8') as file:
        #     text = file.read()

        # # Remove all emojis by replacing them with an empty string
        # clean_text = emoji.replace_emoji(text, replace='')
        # finished_text = re.sub(r"<[^>]*>", "", clean_text)

        # with open("memory_bank/th_data.txt", "w", encoding='utf-8') as file:
        #     file.write(finished_text)

        # return 'All clean!'
                