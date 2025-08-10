# Standard imports.
from PIL import Image
from io import BytesIO

# AI imports.
from google import genai
from google.genai import types

# Custom imports.
from lib.env.settings import GEMINI_API_KEY

class Image_Gen:

    def generate(self, channel:int, content:str):
        client = genai.Client(api_key=GEMINI_API_KEY)
        channel = str(channel)

        try:
            response = client.models.generate_content(
                # model="gemini-2.0-flash-exp",
                model="gemini-2.0-flash-preview-image-generation",
                contents=content,
                config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
            )

        except Exception as e:
            error_catch = str(e)[0:3]

            if error_catch == '429':
                return 'Sorry pictures are done for today.'
            
            else:
                return "Sorry I can't process this picture."
            
        image_binary = response.candidates[0].content.parts[1].inline_data
        image = Image.open(BytesIO(image_binary.data))
        image.save(f'{channel}.png')
