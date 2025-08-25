# AI imports.
from google import genai

# Standard imports.
import sqlite3

# Custom imports.
from lib.env.settings import GEMINI_API_KEY

class Mod:

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)


    def save_game_data(self, name:str, data:str):
        """ Currently using text file for ease of personal modification. If called save requested game data to file.
        """

        data = self.client.models.generate_content(
            model="gemini-2.5-flash", contents=f"This is an image descriptioin {data}. Show me this data removing any redunant text. I want the facts without all the filler."
            )

        with open('memory_bank/game_data.txt', 'a', encoding='utf-8') as file:
            file.write(f'"name": "{name}",\n"data": "{data}",\n\n')

        fun_comment = self.client.models.generate_content(
            model="gemini-2.5-flash", contents=f"let them know the data has been saved. Summarize in 10 words or less then make fun of them."
            )

        return fun_comment.text
    

    def return_game_data(self, channel:int, query:str):
        """ Return game related answer from game memory.
        """

        chat_memory = ''

        conn = sqlite3.connect('memory_bank/mod_memory.db')
        c = conn.cursor()        

        c.execute("SELECT chat_memory FROM Memory WHERE channel = ?", (channel,))
        chat_memory = c.fetchall()[0][0]

        with open('memory_bank/game_data.txt', 'r', encoding='utf-8') as file:
            data = file.read()

        response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=f"Read the following conversation and data and provide an answer for the question - Conversation: {chat_memory} -- Data: {data} -- Question: {query}"
                )

        return response.text      