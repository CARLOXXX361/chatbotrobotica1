from pydantic import BaseModel, Field
from typing import Optional, Type
from langchain.tools import format_tool_to_openai_function, BaseTool
import requests


class Get_City(BaseModel):
    """Entrada de la ciudad."""

    city: str = Field(..., description="Nombre de la ciudad la cual quiere saber la temperatura")


class Weather(BaseTool):
    name = "get_weather"
    description = "Obtener el clima actual"

    def _run(self, city: str):
        response = requests.get(f"http://api.weatherapi.com/v1/current.json?key=cafc59956d6a49979c9172649232007&q={city}&aqi=no")
        if response.status_code == 200:
            temp=response.json()["current"]["temp_c"]
            condition= response.json()["current"]["condition"]["text"]
            humedad= response.json()["current"]["humidity"] 
            tiempo=response.json()["location"]["localtime"] 
            
            finalresult = (str(temp)+" Grados Celcius, " + condition + " , " + str(humedad) + "% humidity"
                           
                           )
            return finalresult
        else:
            print(f"Oops, algo salió mal al llamar al API del clima. Codigo fue: {response.status_code}")

    def _arun(self, city: str):
        pass

    args_schema: Optional[Type[BaseModel]] = Get_City