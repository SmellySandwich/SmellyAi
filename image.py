# Standard imports.
from PIL import Image
from io import BytesIO
from PIL import Image


# AI imports.
from google import genai
from google.genai import types

# Custom imports.
from lib.env.settings import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


# response = client.models.generate_images(
#     # model="imagen-4.0-generate-001",
#     model="gemini-2.5-flash-image-preview",
#     prompt=f"{content[2:]}",
#     config=types.GenerateImagesConfig(number_of_images=1)
# )

pic = input("Enter your shit: ")

response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=pic
    )

data = response.candidates[0].content.parts[0].inline_data.data
# print(data)
image = Image.open(BytesIO(data))
image.show()

# for part in response.parts:
#     if part.inline_data is not None:
#         # Convert the inline data to an image
#         image_data = part.inline_data.data
#         image = Image.open(BytesIO(image_data))
#         # Display the image
#         image.show()