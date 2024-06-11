from socket import timeout
import telebot
import random
from datetime import datetime, timedelta
import logging
import tkinter as tk
import random
from langchain.schema import HumanMessage, AIMessage, ChatMessage, FunctionMessage
from langchain.chains.conversation.memory import ConversationBufferMemory,ConversationBufferWindowMemory
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.agents import initialize_agent, Tool, AgentType,AgentExecutor,OpenAIFunctionsAgent,load_tools
from termcolor import colored
from langchain.utilities import WikipediaAPIWrapper,OpenWeatherMapAPIWrapper
import time  
import threading
import json
from chat import guardar_inputlang_en_json
from cargachat import cargar_inputlang_desde_json
#------------------------------------------------------ tools librerias ------------------------------------------------------
from CLIMA import Weather
from indicadores import Indicadores
from googlesearchgpt import Google_Busqueda
#from yolodetect import PhotoDetectionTool
from stabledifusion import StableDiffusion
from citywatch import Clock
from guardadoconversacion import guardado_conversacion
from WolframAlphaTool import WolframTool
from chatid import guardar_chat_id
from cargarchatid import cargar_chat_ids
from threading import Timer
import multiprocessing
import PySimpleGUI as sg
import os
from yolodetect import PhotoDetectionTool
versionbot="0.35"


message_json=""
wikipedia = WikipediaAPIWrapper(lang="en",doc_content_chars_max=250)
wikipedia_tool = Tool(
    name='wikipedia',
    func= wikipedia.run,
    description="esta herramienta es perfecta cuando necesitas buscar información resumida en wikipedia sobre temas, países o personas,etc.")

OPENAI_API_KEY = "apikey"

llm = ChatOpenAI(
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY,
    model_name='gpt-3.5-turbo-0613',
    max_tokens= 200
)


system_message = SystemMessage(content="Eres un asistente amigable, ademas respondes con emojis a cada pregunta, debe dar respuestas breves y concisa, y tienes una herramienta con la cual puedes ver objetos y personas cuando te lo requieran")
prompt = OpenAIFunctionsAgent.create_prompt(system_message=system_message)

MEMORY_KEY = "chat_history"

prompt = OpenAIFunctionsAgent.create_prompt(
    system_message=system_message,
    extra_prompt_messages=[MessagesPlaceholder(variable_name=MEMORY_KEY)])


memory = ConversationBufferWindowMemory(k=4,memory_key=MEMORY_KEY, return_messages=True)

tools = ([Clock(),Weather(),Indicadores(),Google_Busqueda(),wikipedia_tool,WolframTool(),StableDiffusion(),PhotoDetectionTool()])  # TOOLS PARA DIFERENTES COSAS ,PhotoDetectionTool(),StableDiffusion()

agent = OpenAIFunctionsAgent(llm=llm, tools=tools,prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True, max_iterations=7, handle_parsing_errors="ERROR", max_execution_time=40)

bot_token = "BOTTOKEN-TELEGRAM"

logging.basicConfig(level=logging.INFO)

conversacion = {}
bot = telebot.TeleBot(bot_token)

  
def codigo_verificacion():
    global verification_code
    verification_code = random.randint(1000, 9999)
    print(f"Código de verificación inicial generado: {verification_code}")

def actualizar_codigos_verificacion():
    global verification_code
    for chat_id in conversacion:
        conversacion[chat_id]['verification_code'] = verification_code
def lol2():
    global inputlang
    lol = (str(inputlang))


codigo_verificacion()
# Manejar mensajes de texto
conversacion_en_curso = False
cronometro_corriendo = False
enviando_mensaje = False
conversacion2 = []
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global user_input
    user_input = message.text
    print(user_input)
    chat_id = message.chat.id


    global verification_code
    actualizar_codigos_verificacion()
    def cronometro():
        global segundos, cronometro_corriendo
        while cronometro_corriendo: 
            if segundos >= 180:
                if cronometro_corriendo:  # Verifica que cronometro_corriendo todavía es True antes de ejecutar el código
                    agent_executor.memory.clear()  # Borra Memoria
                    codigo_verificacion()
                    conversacion[chat_id]['verification_code'] = verification_code
                    conversacion[chat_id]['estado'] = 'Esperando_Verificacion'
                    bot.send_message(chat_id, f"Conversación completada. Por favor, *ingrese el nuevo código* 🔐", parse_mode="markdown")
                    logging.info(f"Fin de la conversación en el chat {chat_id}.")
                    actualizar_codigos_verificacion() #Actualizo los codigos de verificacion de mis arrays
                    print (conversacion)
                    cronometro_corriendo = False  # Cambia cronometro_corriendo a False
                segundos = 0  # Reinicia el contador
            elif cronometro_corriendo:
                #print(f'Tiempo transcurrido: {segundos} segundos')
                segundos += 1
                time.sleep(1)

    def iniciar_cronometro():
        global cronometro_corriendo, segundos
        if not cronometro_corriendo:
            cronometro_corriendo = True
            segundos = 0 
            hilo_cronometro = threading.Thread(target=cronometro)
            hilo_cronometro.start()
        else:
            while cronometro_corriendo:
                time.sleep(1)


    global conversacion_en_curso
    if conversacion_en_curso:
        bot.send_message(chat_id, "Hay un chat en conversación. Por favor, espere su turno.")
    else:
        if chat_id not in conversacion:
            # Es una nueva conversación, usar el código generado al inicio y guardarlo en el diccionario
            bot.send_message(chat_id, "Ingresa nuevamente el código de verificación de 4 dígitos para iniciar la conversación.")
            conversacion[chat_id] = {'estado': 'Esperando_Verificacion', 'verification_code': verification_code}
            print (conversacion)
        else:
            estado = conversacion[chat_id]['estado']
            #hay_espera_verificacion = any(chat['estado'] == 'Esperando_Verificacion' for chat in conversacion.values())
            hay_en_conversacion = any(chat['estado'] == 'en_conversacion' for chat in conversacion.values())

            if estado == "Esperando_Verificacion":
                if hay_en_conversacion:
                    bot.send_message(chat_id, "*Hay un chat en conversación. Por favor, espere su turno.*",parse_mode="markdown")
                else:
                    verification_code = conversacion[chat_id]['verification_code']
                    if user_input == str(verification_code):
                        guardar_chat_id(chat_id)
                        cargar_chat_ids()
                        bot.send_message(chat_id, "✅ *Código correcto* - ¡Comienza la conversación! Dispones de *3 minutos*. Realizame preguntas.",parse_mode="markdown")
                        conversacion[chat_id]['estado'] = 'en_conversacion'
                        conversacion[chat_id]['start_time'] = datetime.now()
                        logging.info(f"Inicio de la conversación en el chat {chat_id}.")
                        iniciar_cronometro()
                    else:
                        if user_input == "/tools":
                            chat_id = message.chat.id
                            bot.send_message(chat_id, """\
                        🛠️ Herramientas\n*Este bot dispone de las siguientes herramientas:*\n-☀️ Clima\n-💲 Indicadores Económicos\n-🔍 Búsqueda en Google\n-🖼️ Generador de imágenes con Stable Diffusion XL\n-🧮 Wolfram Alpha\n-🕰 Reloj\n-📚 Wikipedia\n-👀 Visión con Yolov5 y Blip-2""",parse_mode="markdown")
                        elif user_input == "/start":
                            chat_id = message.chat.id
                            bot.send_message(chat_id, "🚀 *Bienvenido a nuestro asistente!\n*Para comenzar, ingresa el código que aparece en pantalla. El bot te lo solicitará nuevamente, y podrás disfrutar de una interacción de *3 minutos*.Recuerda que solo un usuario puede interactuar a la vez, así que si el bot no responde en algún momento, no dudes en hacer otra pregunta. ¡Estamos aquí para ayudarte!",parse_mode="markdown")
                        elif user_input == "/info":
                            chat_id = message.chat.id
                            bot.send_message(chat_id, """ℹ️ *Información:*\nEste es un 🤖 bot con inteligencia artificial del laboratorio de robótica de la PUCV. *¡Hazle preguntas y te responderá!*""",parse_mode="markdown")
                        elif user_input == "/by":
                            chat_id = message.chat.id
                            bot.send_message(chat_id, """👤 *Creado por:*\nCarlos Zamorano (Colaborador Lab).""",parse_mode="markdown")
                        elif user_input == "/version":
                            chat_id = message.chat.id
                            bot.send_message(chat_id, f"""📅 Versión: *Beta {versionbot}*""",parse_mode="markdown")
                        elif user_input == "/ejemplos":
                            ejemplo=random.randint(1,6)
                            chat_id = message.chat.id
                            if ejemplo == 1:
                                bot.send_message(chat_id, """Generame una imagen de un robot""",parse_mode="markdown")
                                time.sleep(0.5)
                                bot.send_photo(chat_id, photo=open('ejemplo.jpg', 'rb'))
                            elif ejemplo == 2:
                                bot.send_message(chat_id, """Cual es el clima en valparaiso""",parse_mode="markdown")
                                time.sleep(0.5)
                                bot.send_message(chat_id, """El clima en Valparaíso es de 21.0 grados Celsius, soleado y con un 49% de humedad. ☀""",parse_mode="markdown")
                            elif ejemplo == 3:
                                bot.send_message(chat_id, """Que es la ley de ohm""",parse_mode="markdown")
                                time.sleep(0.5)
                                bot.send_message(chat_id, """La Ley de Ohm es una ley fundamental en la electricidad que establece la relación entre la corriente eléctrica, la resistencia y la tensión en un circuito eléctrico. Fue formulada por el físico alemán Georg Simon Ohm en 1827. Según esta ley, la corriente eléctrica que fluye por un conductor es directamente proporcional a la tensión aplicada e inversamente proporcional a la resistencia del circuito. Matemáticamente, se expresa como I = V/R........""",parse_mode="markdown")
                            elif ejemplo == 4:
                                bot.send_message(chat_id, """Hazme un cuadro colorido estilo Kandinsky de puras figuras geometricas y hiperplanos""",parse_mode="markdown")
                                time.sleep(0.5)
                                bot.send_photo(chat_id, photo=open('ejemplo2.jpg', 'rb'))
                            elif ejemplo == 5:
                                bot.send_message(chat_id, """Cuánto es x^2 +1=x/3+6""",parse_mode="markdown")
                                time.sleep(0.5)
                                bot.send_message(chat_id, """La solución de la ecuación x^2 + 1 = x/3 + 6 es: x = 1/6 (1 - √181)""",parse_mode="markdown")
                            elif ejemplo == 6:
                                bot.send_message(chat_id, """Que ves?""",parse_mode="markdown")
                                time.sleep(0.5)
                                bot.send_message(chat_id, """Puedo ver una persona sentada en una sala""",parse_mode="markdown")
                        else:
                            bot.send_message(chat_id, "Código incorrecto. Inténtalo de nuevo.")
                            print(f"Ingresa el nuevo código de verificación: {verification_code}")
                            print (conversacion)
            elif estado == "en_conversacion":
                print (conversacion)
                current_time = datetime.now()
                start_time = conversacion[chat_id]['start_time']
                elapsed_time = current_time - start_time
                if user_input == "/tools":
                    chat_id = message.chat.id
                    bot.send_message(chat_id, """\
                🛠️ Herramientas\n*Este bot dispone de las siguientes herramientas:*\n-☀️ Clima\n-💲 Indicadores Económicos\n-🔍 Búsqueda en Google\n-🖼️ Generador de imágenes con Stable Diffusion XL\n-🧮 Wolfram Alpha\n-🕰 Reloj\n-📚 Wikipedia\n-👀 Visión con Yolov5 y Blip-2""",parse_mode="markdown")
                    logging.info(f"Tiempo transcurrido en el chat {chat_id}: {elapsed_time}")
                elif user_input == "/start":
                    chat_id = message.chat.id
                    bot.send_message(chat_id, "🚀 *Bienvenido a nuestro asistente!\n*Para comenzar, ingresa el código que aparece en pantalla. El bot te lo solicitará nuevamente, y podrás disfrutar de una interacción de *2️⃣ minutos*.Recuerda que solo un usuario puede interactuar a la vez, así que si el bot no responde en algún momento, no dudes en hacer otra pregunta. ¡Estamos aquí para ayudarte!",parse_mode="markdown")
                    logging.info(f"Tiempo transcurrido en el chat {chat_id}: {elapsed_time}")
                elif user_input == "/info":
                    chat_id = message.chat.id
                    bot.send_message(chat_id, """ℹ️ *Información:*\nEste es un 🤖 bot con inteligencia artificial del laboratorio de robótica de la PUCV. *¡Hazle preguntas y te responderá!*""",parse_mode="markdown")
                    logging.info(f"Tiempo transcurrido en el chat {chat_id}: {elapsed_time}")
                elif user_input == "/by":
                    chat_id = message.chat.id
                    bot.send_message(chat_id, """👤 *Creado por:*\nCarlos Zamorano (Colaborador Lab).""",parse_mode="markdown")
                    logging.info(f"Tiempo transcurrido en el chat {chat_id}: {elapsed_time}")
                elif user_input == "/ejemplos":
                    ejemplo=random.randint(1,5)
                    chat_id = message.chat.id
                    if ejemplo == 1:
                        bot.send_message(chat_id, """Generame una imagen de un robot""",parse_mode="markdown")
                        time.sleep(0.5)
                        bot.send_photo(chat_id, photo=open('ejemplo.jpg', 'rb'))
                    elif ejemplo == 2:
                        bot.send_message(chat_id, """Cual es el clima en valparaiso""",parse_mode="markdown")
                        time.sleep(0.5)
                        bot.send_message(chat_id, """El clima en Valparaíso es de 21.0 grados Celsius, soleado y con un 49% de humedad. ☀""",parse_mode="markdown")
                    elif ejemplo == 3:
                        bot.send_message(chat_id, """Que es la ley de ohm""",parse_mode="markdown")
                        time.sleep(0.5)
                        bot.send_message(chat_id, """La Ley de Ohm es una ley fundamental en la electricidad que establece la relación entre la corriente eléctrica, la resistencia y la tensión en un circuito eléctrico. Fue formulada por el físico alemán Georg Simon Ohm en 1827. Según esta ley, la corriente eléctrica que fluye por un conductor es directamente proporcional a la tensión aplicada e inversamente proporcional a la resistencia del circuito. Matemáticamente, se expresa como I = V/R........""",parse_mode="markdown")
                    elif ejemplo == 4:
                        bot.send_message(chat_id, """Hazme un cuadro colorido estilo Kandinsky de puras figuras geometricas y hiperplanos""",parse_mode="markdown")
                        time.sleep(0.5)
                        bot.send_photo(chat_id, photo=open('ejemplo2.jpg', 'rb'))
                    elif ejemplo == 5:
                        bot.send_message(chat_id, """Cuánto es x^2 +1=x/3+6""",parse_mode="markdown")
                        time.sleep(0.5)
                        bot.send_message(chat_id, """La solución de la ecuación x^2 + 1 = x/3 + 6 es: x = 1/6 (1 - √181)""",parse_mode="markdown")
                    elif ejemplo == 6:
                        bot.send_message(chat_id, """Que ves?""",parse_mode="markdown")
                        time.sleep(0.5)
                        bot.send_message(chat_id, """Puedo ver una persona sentada en una sala""",parse_mode="markdown")
                elif user_input == "/version":
                    chat_id = message.chat.id
                    bot.send_message(chat_id, f"""📅 Versión: *Beta {versionbot}*""",parse_mode="markdown")
                    logging.info(f"Tiempo transcurrido en el chat {chat_id}: {elapsed_time}")
                
                    
                else:
                    global enviando_mensaje
                    chat_id = message.chat.id
                    if not enviando_mensaje:
                        # Marca que se está enviando un mensaje
                        enviando_mensaje = True
                        global inputlang
                        inputlang = agent_executor.run(user_input)
                        guardar_inputlang_en_json(inputlang)
                        # Enviar el mensaje
                        bot.send_message(chat_id, inputlang)
                        conversacion2.append({"Pregunta": user_input})
                        conversacion2.append({"Asistente": inputlang})
                        enviando_mensaje = False
                        print(conversacion2)
                    logging.info(f"Tiempo transcurrido en el chat {chat_id}: {elapsed_time}")

ventanaconver = []
user_input = ""
last_user_input = user_input
def ventana():
    global last_user_input
    image_ruta = 'qrcode.png'
    font_size = 50
    window_size = (1080, 1920)
    sg.theme('DarkBrown2')
    imagenultipath='ejemplos/ultima.png'

    columna = [
        [sg.Text(f"CHATEA CONMIGO!", text_color='white', font=('Helvetica', font_size))],
    ]

    mensaje = [
        [sg.Text(f"Con este QR podrás ingresar al bot", font=('Any', 20))],
    ]
    imagenqr= [
        [sg.Image(filename=image_ruta, size=(250, 250), key='-IMAGE-')],
    ]
    codeveri= [
        [sg.Text(f"Código de Verificacion: {verification_code}", font=('Any', 40), key='-LABEL-')],
    ]
    columna2 = [
        [sg.Text(f"Descarga Telegram, escanea el código QR para acceder al bot y luego introduce el código de verificación", font=('Any', 16))],
    ]

    columna3 = [
        [sg.Multiline(size=(45, 20), enter_submits=False, key='-QUERY-', do_not_clear=True, autoscroll=True, font=('Helvetica', 15), text_color='black')],
    ]
    mesaimage= [
        [sg.Text(f"Última imagen generada: ", font=('Any', 20))],
    ]
    ultimage= [
        [sg.Image(filename=imagenultipath, key='-IMAGEul-', size=(700, 700))],
    ]
    chat= [
        [sg.Text(f"Chat:", font=('Any', 20))],
    ]
    layout = [
        [sg.Column(columna, justification='center')],
        [sg.Column(columna2, justification='center')],
        [sg.Column(mensaje, justification='center')],
        [sg.Column(imagenqr, justification='center')],
        [sg.Column(codeveri, justification='center')],
        [sg.Column(mesaimage, element_justification='c')],
        [sg.Column(ultimage, element_justification='c')],
        #[sg.Column(chat, element_justification='c')],
        [sg.Column(columna3, justification='center')]
        #[sg.Button('Cerrar')]
    ]
    

    #print(message_json)
    window = sg.Window('GUI:', layout, finalize=True, size=window_size, element_justification='c')
    while True:
        sg.set_options(suppress_error_popups = True)
        event, values = window.read(timeout=1)  # Actualizar cada 1000 ms (1 segundo)
        if event in (sg.WIN_CLOSED, 'Cerrar'):
            break

        formatted_conversation = '\n\n'.join([f"{list(item.keys())[0]}: {list(item.values())[0]}" for item in conversacion2])
        window['-QUERY-'].update(formatted_conversation)
        window['-LABEL-'].update(f"Codigo de Verificación: {verification_code}")
        window['-IMAGEul-'].update(filename=imagenultipath)
    window.close()


if __name__ == "__main__":
    hilo_cronometro = threading.Thread(target=ventana)
    hilo_cronometro.start()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
