# Standard imports.
from PIL import Image
from io import BytesIO
import random

# AI imports.
from google import genai
from google.genai import types

# Custom imports.
from lib.env.settings import GEMINI_API_KEY

class Image_Gen:

    async def generate(self, channel:int, content:str):
        client = genai.Client(api_key=GEMINI_API_KEY)
        channel = str(channel)

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=f"{content}",
                config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
            )

        except Exception as e:
            print(f'Error in genimage.py: {e}\n')
            return "Sorry I can't process this picture."
        
        file_name = random.randint(1, 100000)
        image_binary = response.candidates[0].content.parts[1].inline_data
        image = Image.open(BytesIO(image_binary.data))
        image.save(f'{file_name}.png')

        return file_name
