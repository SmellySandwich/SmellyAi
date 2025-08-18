# AI imports.
from google import genai

# Custom imports.
from lib.env.settings import GEMINI_API_KEY

class Mod:

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)


    def save_game_data(self, name:str, data:str):
        """ Currently using text file for ease of personal modification. If called save requested game data to file.
        """

        with open('memory_bank/game_data.txt', 'a', encoding='utf-8') as file:
            file.write(f'"name": "{name}",\n"data": "{data}",\n\n')

        fun_comment = self.client.models.generate_content(
            model="gemini-2.5-flash", contents=f"let {name} know the data has been saved in a funny way in 10 words or less."
            )

        return fun_comment.text
    

    def return_game_data(self, query:str):
        """ Return game related answer from game memory.
        """

        with open('memory_bank/game_data.txt', 'r', encoding='utf-8') as file:
            data = file.read()

        response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=f"Read the following data and provide an aswer in 500 words or less for the question - Data: {data}  - Question: {query}"
                )

        return response.text      