from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
from langchain.tools import BaseTool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate
import requests
import replicate
from cargarchatid import cargar_chat_ids
import telebot
import datetime
from PIL import Image
def redimen():
    input_image_path = "ejemplos/ultima.png"
    output_image_path = "ejemplos/ultima.png"
    img = Image.open(input_image_path)
    new_width = 350
    new_height = 350
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
        
        bot_token = 'TOKENTELEGRAMBOT'  
        telebot.TeleBot(bot_token).send_message(chat_id, f"🖼️*Creando Imagen.....*",parse_mode='Markdown')
        telebot.TeleBot(bot_token).send_message(chat_id, f"*Espere un Momento*",parse_mode='Markdown')

        output = replicate.run(" TOKEN REPLICATE ",
        input={"prompt": f"{query}"})

        image = output[0]

        current_time = datetime.datetime.now()
        fecha_str = current_time.strftime("%d-%m-%Y")
        time_str = current_time.strftime("%H;%M;%S")

        imagen_local = f"photos-Stabled/{fecha_str}-{time_str}.png" # El nombre con el que queremos guardarla
        imagenultima = f"ejemplos/ultima.png"
        imagen = requests.get(image).content
        with open(imagen_local, 'wb') as handler:
            handler.write(imagen)
        with open(imagenultima, 'wb') as handler:
            handler.write(imagen)
            redimen()


        # Luego, ejecuta el enlace URL
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto?chat_id={chat_id}&photo={image}"
        response = requests.get(url)

        # Verificar si la solicitud al enlace URL fue exitosa
        if response.status_code == 200:
            print("Enlace imagen enviada exitosamente")
            telebot.TeleBot(bot_token).send_message(chat_id, f"Imagen de {query} creada.",parse_mode='Markdown')
            return "Imagen Generada"
            
        else:
            print("Error al ejecutar")
            return "Error al generar imagen intente nuevamente"
