from pydantic import BaseModel, Field
from typing import Optional, Type
from langchain.tools import BaseTool
import requests


class Get_Clock(BaseModel):
    """Entrada de la ciudad."""
    country: str = Field(..., description="Nombre de la ciudad la cual quiere saber la hora y fecha actual, si el usuario no pide una ubicacion en concreto, se ingresará 'chile' por default")

class Clock(BaseTool):
    name = "get_Clock"
    description = "Obtener la hora actual y dia actual de un pais o ciudad del mundo"

    def _run(self, country: str):
        response = requests.get(f"https://timezone.abstractapi.com/v1/current_time/?api_key=67ee0bd504554aeb860b55bae5f51089&location={country}")
        if response.status_code == 200:
            datetime=response.json()["datetime"]
            finalresult = ("La hora y fecha es: " + str(datetime)+ " en " + country)
            return finalresult
        else:
            print(f"Oops, algo salió mal al llamar al API del clima. Codigo fue: {response.status_code}")

    def _arun(self, country: str):
        pass

    args_schema: Optional[Type[BaseModel]] = Get_Clock