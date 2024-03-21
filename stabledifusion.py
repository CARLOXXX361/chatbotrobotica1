import base64
import requests
import os
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
from langchain.tools import BaseTool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate
import requests
from cargarchatid import cargar_chat_ids
import telebot
from PIL import Image
import random


def redimen(input):
    input_image_path = f"{input}"
    output_image_path = "ejemplos/ultima.png"
    img = Image.open(input_image_path)
    new_width = 700
    new_height = 700
    resized_img = img.resize((new_width, new_height))
    resized_img.save(output_image_path)


class StableDiffusion(BaseTool):
    name = "get_imagen"
    description = "Genera imágenes digitales de alta calidad a partir de descripciones en lenguaje natural y se usa esa descripción como query"
    return_direct = True
    def _run(self, query: str, text: str = None, url: str = None, description: str = None):
        chat_ids=cargar_chat_ids()
        for chat_id in chat_ids:
            print(chat_id)
        
        bot_token = '6397055999:AAHSlOzmdu9eTRcx-cN1sRWtN6nso6X2cmg'  
        bot = telebot.TeleBot(bot_token)
        telebot.TeleBot(bot_token).send_message(chat_id, f"🖼️*Creando Imagen.....*",parse_mode='Markdown')
        telebot.TeleBot(bot_token).send_message(chat_id, f"*Espere un Momento*",parse_mode='Markdown')

        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        body = {
            "steps": 40,
            "width": 1024,
            "height": 1024,
            "seed": 0,
            "cfg_scale": 5,
            "samples": 1,
            "text_prompts": [
                {
                "text": f"{query}",
                "weight": 1
                },
                {
                "text": "blurry, bad",
                "weight": -1
                }
            ],
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-JY7n1eptQhzGjC7jPQoSXbhKxpGwcr08liUzO3gzDWk97DeO",
        }

        response = requests.post(
            url,
            headers=headers,
            json=body,
        )

        if response.status_code == 200:
            data = response.json()

            out_directory = "./photos-Stabled"

            if not os.path.exists(out_directory):
                os.makedirs(out_directory)

            for i, image in enumerate(data["artifacts"]):
                with open(f'{out_directory}/txt2img_{image["seed"]}.png', "wb") as f:
                    f.write(base64.b64decode(image["base64"]))

            with open(f'{out_directory}/txt2img_{image["seed"]}.png', "rb") as photo:
                bot.send_photo(chat_id, photo)
                redimen(f'{out_directory}/txt2img_{image["seed"]}.png')
            bot.send_message(chat_id, f"Foto de {query} creada con exito.")
            return "Imagen generada y enviada con éxito"
        else:
            error_message = f"Error en la generación de imagen. Su petición contiene contenido inapropiada para usuarios sensibles intente nuevamente ERROR 400"
            print(error_message)
            return error_message