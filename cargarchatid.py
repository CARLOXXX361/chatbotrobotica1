import os
import json
file_path = "chatid.json"  # Ruta del archivo JSON
def cargar_chat_ids():
    return json.load(open(file_path)) if os.path.isfile(file_path) else []
