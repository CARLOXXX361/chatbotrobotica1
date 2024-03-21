import os
import json
import datetime

def guardado_conversacion(question, respuesta):
    current_time = datetime.datetime.now()
    date_str, time_str = current_time.strftime("%d-%m-%Y"), current_time.strftime("%H:%M:%S")
    dj = f"conversation/{date_str}.json"
    
    interaction = {
        "Fecha": time_str,
        "Pregunta": question,
        "Respuesta": respuesta
    }
    
    mode = 'r+' if os.path.isfile(dj) else 'w'
    
    with open(dj, mode, encoding="utf-8") as file:
        data = json.load(file) if mode == 'r+' else []
        data.append(interaction)
        file.seek(0)
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.truncate()
