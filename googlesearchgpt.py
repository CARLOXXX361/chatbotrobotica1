import requests
from typing import Optional
from langchain.tools import BaseTool
import json
from langchain.callbacks.manager import CallbackManagerForToolRun

class Google_Busqueda(BaseTool):

    name = "get_search"
    description = "Herramienta de búsqueda de información basada en el motor de Google que brinda respuestas precisas y actualizadas al día sobre edades, fechas y una amplia gama de temas"

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun]=None):
        url = "https://google.serper.dev/search"
        busqueda = query  # ARGUMENTO QUE USARÁ PARA REALIZAR LA BÚSQUEDA
        payload = json.dumps({
            "q": busqueda,
            "gl": "cl",
            "hl": "es-419"
        })
        headers = {
            'X-API-KEY': 'b2ead19cdc3b009d85d5d004ad0838fa689ef962',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        packages_json = response.json()
        if response.status_code == 200:
            # Obtener el contenido del "answerBox" si está presente en la respuesta
            answer_box = packages_json.get('answerBox',None)
            if answer_box:

                answer_box_results = {
                    "title": answer_box.get('title', ''),
                    "answer": answer_box.get('answer', ''),
                    "snippet": answer_box.get('snippet', '')  # Puedes agregar 'snippet' si existe
                }
            else:
                answer_box_results = None
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
             # Obtener los primeros 3 resultados del apartado "organic"
            organic = packages_json.get('organic', [])[:3]
            organic_results = []

            for index, result in enumerate(organic):
                result_info = {
                    "title": result.get('title', ''),
                }
                if index == 0:
                    result_info["link"] = result.get('link', '')
                    result_info["snippet"] = result.get('snippet', '')
                organic_results.append(result_info)

            return {
                "answerBox": answer_box_results,
                "organic_results": organic_results
            }
        else:
            print(f"ERROR AL CONECTARSE A LA API, INTENTE MAS TARDE, CODIGO: {response.status_code}")

    def _arun(self, arg: str):
        
        pass
