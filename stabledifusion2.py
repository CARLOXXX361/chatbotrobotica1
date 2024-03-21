from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
from langchain.tools import BaseTool
import torch
from PIL import Image
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate
import subprocess
import requests
from cargarchatid import cargar_chat_ids
import datetime
import telebot


model_id = "stabilityai/stable-diffusion-2-1"
scheduler = EulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
pipe = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
pipe = pipe.to("cuda")


class StableDiffusion(BaseTool):
    name = "get_imagen"
    description = "Genera imágenes digitales de alta calidad a partir de descripciones en lenguaje natural y se usa esa descripción como query"
    return_direct=True
    def _run(self, query: str, text: str = None, url: str = None, description: str = None):
        bot_token = '6397055999:AAHSlOzmdu9eTRcx-cN1sRWtN6nso6X2cmg'

        chat_ids=cargar_chat_ids()
        for chat_id in chat_ids:
            print(chat_id)
    

        if query is not None:
            input_text = query
        elif text is not None:
            input_text = text
        elif url is not None:
            input_text = url
        elif description is not None:
            input_text = query
        else:
            raise ValueError("Se debe proporcionar 'query' o 'text' como argumento.")
        

        telebot.TeleBot(bot_token).send_message(chat_id, f"🖼️*Creando Imagen.....*",parse_mode='Markdown')
        telebot.TeleBot(bot_token).send_message(chat_id, f"*Espere un Momento*",parse_mode='Markdown')

        
        prompt = str(input_text)
        image = pipe(prompt).images[0]
        lista = ["/", ":", "<", "$", ">", "“", "|", "?", "*"]
        current_time = datetime.datetime.now()
        fecha_str = current_time.strftime("%d-%m-%Y")
        time_str = current_time.strftime("%H;%M;%S")
        for char in lista:
            if char in prompt:
                prompt = prompt.replace(char, "")
        imageFile = f'photos-Stabled/{fecha_str}-{time_str}.png'
        image.save(imageFile)
        url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'

        # Crear un diccionario con los datos que se enviarán en el formulario
        data = {'chat_id': chat_id}

        # Abrir y enviar la foto como un archivo binario
        with open(imageFile, 'rb') as photo:
            files = {'photo': photo}
            response = requests.post(url, data=data, files=files)
        
        # Verificar la respuesta
        if response.status_code == 200:
            print('La foto se envió con éxito.')
        else:
            print(f'Ocurrió un error al enviar la foto. Código de estado HTTP: {response.status_code}')

        return "Imagen Generada"