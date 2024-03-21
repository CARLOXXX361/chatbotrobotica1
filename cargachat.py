import json

def cargar_inputlang_desde_json():
    try:
        # Abrir el archivo "chat.json" en modo lectura
        with open('chat.json', 'r', encoding='utf-8') as json_file:
            # Cargar el contenido del archivo JSON como una lista
            data = json.load(json_file)
            # Obtener el primer elemento de la lista
            if data:
                inputlang = data[0]
                return inputlang
            else:
                return None
    except FileNotFoundError:
        # Manejar el caso en que el archivo no existe
        print("El archivo 'chat.json' no existe.")
        return None
    except json.JSONDecodeError:
        # Manejar errores de decodificación JSON
        print("Error al decodificar el archivo JSON.")
        return None

