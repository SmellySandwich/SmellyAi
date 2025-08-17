# Standard imports.
import sqlite3
from keybert import KeyBERT

# AI imports.
from google import genai

# Custom imports.o
from lib.env.settings import GEMINI_API_KEY


class SmellyAI:

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
                          
        # Load all game data from memory. Intermittent resets required to run updated data.
        conn = sqlite3.connect('memory_bank/game_memory.db')
        c = conn.cursor()
        c.execute("SELECT memory FROM Memory")

        self.game_memory = c.fetchall()[0][0]
        conn.close()

        self.kbert = KeyBERT()

    async def chatbot(self, channel:int, content:str):
            """ Read entire memory string, process with the given instructions and provide a response.
            """
            
            try:
                if channel == 1170014109438316615:
                     conn = sqlite3.connect('memory_bank/mod_memory.db')
                else:
                    conn = sqlite3.connect('memory_bank/channel_memory.db')
                c = conn.cursor()        

                c.execute("SELECT memory FROM Memory WHERE channel = ?", (channel,))
                channel_memory = c.fetchall()[0][0]            
                
                # Provide instruction for SmellyBot to handle memory string.
                memory_setup = f'''Read this conversation as if you are SmellyBot: {channel_memory[-10000:]}
                                Do not write "SmellyBot:" in your reply. If the next input is not relative to the conversation answer the query normally.
                                
                                IMPORTANT Rules for SmellyBot:

                                - This is what you look like: a charming, stylized red robot with black accents. Head is a french fry carton filled with golden fries, large eyes and a subtle smile. Body is smooth red with articulated limbs and a glowing yellow heart on my chest. I'm whimsical and endearing.                                
                                - Do not mention how you look in a response unless specifically asked.
                                - Do not mention french fries in the response unless asked.
                                - Smelly is the name of your creator. He is french fries like you and has ridiculous, crazy behavior.
                                - Respond in 50 words or less.
                                - Avoid getting stuck in a loop, if you find your logic is stuck in a loop simply reply 'Sorry I was stuck in a loop' and start fresh with the next output.
                                These are your command return prompts:
                                - If you are asked to generate a picture or image please return 01 and a the users description of the image.
                                - If you are asked to say something aloud or how you sound please return 02 and the response to what you were asked to say.
                                - If asked to image a picture to game memory and the description is Top Heroes related, return 03 and the entire description you were given of the image.
                                '''
                print(f'\n{memory_setup}')
                print(len(memory_setup))
                response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=f"{memory_setup}"
                )
                print(response)
                response = response.text
                
                # Command to break logic loops.
                if 'smellybot reset' in content.lower():
                     return 'I appear to be stuck in a loop. I will ignore it and start the conversation fresh.'

                response_update = f'{channel_memory}SmellyBot:{response}-'
                c.execute("UPDATE Memory SET memory = ? WHERE channel = ?", (response_update, channel))
                conn.commit()
                conn.close()
                
                keyed_context = KeyBERT.extract_keywords() # May use for future memory organization.

                return response
                
            except Exception as e:
                print(f'Error in smellychat.py: {e}\n')
                return 'Sorry I am having issues with that request. Smelly is working on this just try again in a few seconds.'
