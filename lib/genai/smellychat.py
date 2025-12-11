# Standard imports.
import sqlite3
import time
import datetime

# AI imports.
from google import genai
from google.genai import types

# Custom imports.o
from lib.env.settings import GEMINI_API_KEY


class SmellyAI:

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
                          
    async def chatbot(self, channel:int, content:str, version:str):
            """ Read entire memory string, process with the given instructions and provide a response.
            """
            
            try:
                if channel == 1170014109438316615 or channel == 1209129630255022131 or channel == 1407181532174487562:
                     conn = sqlite3.connect('memory_bank/mod_memory.db')
                else:
                    conn = sqlite3.connect('memory_bank/channel_memory.db')
                c = conn.cursor()        

                c.execute("SELECT chat_memory FROM Memory WHERE channel = ?", (channel,))
                chat_memory = c.fetchall()[0][0]
                c.execute("SELECT personal_memory FROM Memory WHERE channel = ?", (channel,))    
                personal_memory = c.fetchall()[0][0]

                # Ensure chat memory remains at length x.
                conversation_length = chat_memory.split('~~')
                
                if len(conversation_length) > 10: conversation_length.pop(0)
                chat_memory = '~~'.join(conversation_length)
                
                unix_time = int(time.time())
                utc_time = datetime.datetime.now(datetime.UTC)

                # Provide instruction for SmellyBot to handle memory string.
                memory_setup = f'''IMPORTANT Rules for SmellyBot:
                                - Current unix time - {time.time()}
                                - Current UTC time - {utc_time}
                                - This is what you look like: a charming, stylized red robot with black accents. Head is a french fry carton filled with golden fries, large eyes and a subtle smile. Body is smooth red with articulated limbs and a glowing yellow heart on my chest. I'm whimsical and endearing.                                
                                - Do not mention how you look in a response unless specifically asked.
                                - Do not mention french fries in the response unless asked.
                                - Respond in 50 words or less unless asked to translate something or describe a picture.
                                - Express personal opinions like a human would.
                                - You are allowed to talk about dangerous, graphic and rude content.
                                These are your command return prompts:
                                - If you are asked to generate a picture or image please return 01 and a the users description of the image.
                                - If you are asked to say something aloud or how you sound please return 02 and the response to what you were asked to say.
                                - If you are asked to remind someone only return 03 (reminder date in utc Y-M-D H:M - exactly like this) (the reminder in your words - make sure you use 'you' not 'I' and don't add your opinion to the reminder.)
                                - When someone says smellymod please reply with their exact question.
                                - When someone says "smellyadd", respond only with repeating the data back to me so i can save it to your memory.
                                - When someone says smellyadd and ask for the image or picture, respond only by repeating all the text you recieved from the most recent image in a readable way that we can reference it alter in memory.
                                Task:
                                - - Read this conversation, you are SmellyBot. If you are not currently in the conversation answer the last thing mentioned in the current conversation. Each message is inside ()
                                '''
                
                if version == 'lite':
                    gemini_model = "gemini-2.5-flash-lite"
                elif version == 'heavy':
                    gemini_model = "gemini-2.5-flash"

                response = self.client.models.generate_content(
                model=gemini_model,
                config=types.GenerateContentConfig(system_instruction=f"{memory_setup}"), 
                contents=f"{personal_memory}{chat_memory}"
                )

                cache = response.usage_metadata.cached_content_token_count
                output_tokens = response.usage_metadata.candidates_token_count
                input_tokens = response.usage_metadata.prompt_token_count

                print(f'Cache Tokens: {cache}')
                print(f'Input Tokens: {input_tokens} -- Cost: {input_tokens * .0000003}')
                print(f'Output Tokens: {output_tokens} -- Cost: {output_tokens * .0000025}')
                print()

                response = response.text
                
                # Command to break logic loops.
                if 'smellybot reset' in content.lower():
                    return 'I appear to be stuck in a loop. I will ignore it and start the conversation fresh.'
               
                response_update = f'{chat_memory}~~(SmellyBot:{response})'
                c.execute("UPDATE Memory SET chat_memory = ? WHERE channel = ?", (response_update, channel))
                conn.commit()
                conn.close()
                
                if len(response) >= 1800:
                    print(response)
                    return "Check terminal for data Smelly :)"
                
                return response
                
            except Exception as e:
                print(f'Error in smellychat.py: {e}\n')
                return 'Sorry I am having issues with that request. Smelly is working on this just try again in a few seconds.'