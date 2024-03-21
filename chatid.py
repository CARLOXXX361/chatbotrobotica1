import os
import json

# Función para guardar el chat_id del último usuario con el que está hablando y eliminar cualquier chat_id previamente guardado
def guardar_chat_id(chat_id):
    file_path = "chatid.json"

    # Crear un diccionario con el chat_id actual
    data = [chat_id]

    # Guardar el chat_id en el archivo JSON
    with open(file_path, "w") as file:
        json.dump(data, file)
    return data