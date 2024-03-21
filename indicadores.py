import requests
from langchain.tools import BaseTool
from typing import Union, Dict, Tuple
from pydantic import BaseModel, Field


class Indicadores(BaseTool):
    name = "get_indicadores"
    description = "Obtiene informacion de los valores del dolar, Euro, UF y el procentaje de deseempleo en chile"

    def _to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
        return (), {}
    
    def _run(self):
        response = requests.get('https://mindicador.cl/api')

        if response.status_code == 200:
            packages_json = response.json()
            dolar = (packages_json['dolar']['valor'])
            euro = (packages_json['euro']['valor'])
            desempleo = (packages_json['tasa_desempleo']['valor'])
            uf = (packages_json['uf']['valor'])
            msg = (" " + ("Dolar: " + ' ' + str(dolar) + ' ' + "Euro: " + ' ' + str(euro) + ' ' "UF: " + ' ' + str(uf) + ' ' + "Desempleo: " + str(desempleo)+"%"))
            return msg
        else:
            print(f"Oops, algo salió mal al llamar al API. Codigo fue: {response.status_code}")

    def _arun(self):
        raise NotImplementedError("get_indicadores no tiene soporte async")