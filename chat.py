import json
def guardar_inputlang_en_json(inputlang):
    # Crear un diccionario con el último valor de inputlang
    message_dict = [inputlang]

    # Abrir el archivo "chat.json" en modo escritura y sobrescribir el contenido
    with open('chat.json', 'w', encoding='utf-8') as json_file:
        # Configurar ensure_ascii en False para que los emojis se vean correctamente
        json.dump(message_dict, json_file, ensure_ascii=False, indent=4)