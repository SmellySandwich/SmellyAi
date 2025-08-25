# Standard imports.
import sqlite3
import ast

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

            if channel == 1170014109438316615 or channel == 1209129630255022131 or channel == 1407181532174487562:
                 conn = sqlite3.connect('memory_bank/mod_memory.db')
            else:
                conn = sqlite3.connect('memory_bank/channel_memory.db')
            c = conn.cursor()

            # Check to see if channel exists.
            c.execute("SELECT chat_memory FROM Memory WHERE channel = ?", (channel,))
            channel_exists = c.fetchall()
            
            if channel_exists: return ('I am already listening.')
            
            else:            
                c.execute("INSERT INTO Memory (channel) VALUES (?)", (channel,))
                conn.commit()
                conn.close()
                
                # return f"Hey there, It's me, SmellyBot! I will get in on the conversation when i hear my name. How about we fill up this chat a bit to warm me up."
                return f"I hope this get's me out of beta!"

    def update_chat_memory(self, channel:int, user_id:int, name:str, content:str):
            """ Chat memory will hold the last 20 conversations.
            """

            if channel == 1170014109438316615 or channel == 1209129630255022131 or channel == 1407181532174487562:
                 conn = sqlite3.connect('memory_bank/mod_memory.db')
            else:
                conn = sqlite3.connect('memory_bank/channel_memory.db')
            c = conn.cursor()        

            c.execute("SELECT chat_memory FROM Memory WHERE channel = ?", (channel,))

            fetch_memory = c.fetchall()
            chat_memory = fetch_memory[0][0]
            smelly_first_output = 'SmellyBot:Greetings! I am SmellyBot, ready to assist with your questions and tasks. How may I help you today in this channel?'        
            
            tuple_insert = f'(user_id:{user_id},name:{name},message:{content})'

            # After Smellybot is called insert first entry to database.
            if chat_memory is None:
                c.execute("UPDATE Memory SET chat_memory = ? WHERE channel = ?", (f'({smelly_first_output})~~{tuple_insert}', channel))
                conn.commit()
                conn.close()

            # If there is a memory, pull the entire string and append the new content. Keep it at 20 messages.              
            else:
                conversation_length = chat_memory.split('~~')
                
                if len(conversation_length) > 10: conversation_length.pop(0)
                chat_memory = '~~'.join(conversation_length)
                # print(chat_memory)
                # print()
                new_memory_string = f'{chat_memory}~~{tuple_insert}'

                c.execute("UPDATE Memory SET chat_memory = ? WHERE channel = ?", (new_memory_string, channel))
                conn.commit()
                conn.close()


    def update_personal_memory(self, channel:int, user_id:int, name:str, content:str):
        """ Personal memory will save the 20 most recent preferences for each channel.
        """
        
        if channel == 1170014109438316615 or channel == 1209129630255022131 or channel == 1407181532174487562:
            conn = sqlite3.connect('memory_bank/mod_memory.db')
        else:
            conn = sqlite3.connect('memory_bank/channel_memory.db')
        c = conn.cursor()        

        c.execute("SELECT personal_memory FROM Memory WHERE channel = ?", (channel,))

        fetch_memory = c.fetchall()
        personal_memory = fetch_memory[0][0]

        content = content[2:] 
        tuple_insert = f'(user_id:{user_id},name:{name},message:{content})'

        # If memory is empty, add point.
        if personal_memory is None:
            
            c.execute("UPDATE Memory SET personal_memory = ? WHERE channel = ?", (f'(user_id:{user_id},name:{name},message:{content})~~', channel))
            conn.commit()
            conn.close()
            
        # If there is a memory, pull the entire string and append the new content. Keep it at 20 memory points.              
        else:
            conversation_length = personal_memory.split('~~')
            
            if len(conversation_length) > 10: conversation_length.pop(0)
            personal_memory = '~~'.join(conversation_length)
            
            new_memory_string = f'{personal_memory}~~{tuple_insert}'

            c.execute("UPDATE Memory SET personal_memory = ? WHERE channel = ?", (new_memory_string, channel))
            conn.commit()
            conn.close()

        fun_comment = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=f"Let us know what you remember. 10 words or less, make it funny and relative to what you remembered."
                )

        return fun_comment.text


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
                model="gemini-2.5-flash", contents=f"Say something funny about updating data in 20 words or less."
                )

            return f'OK! My game memory has been updated:\n\n{response}\n\n{fun_comment.text}'
                