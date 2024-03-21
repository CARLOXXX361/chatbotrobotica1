from langchain.utilities import WolframAlphaAPIWrapper
from langchain.tools import BaseTool
from typing import Union, Dict, Tuple, Optional



class WolframTool(BaseTool):
    name = "Wolfram_get"
    description=("Esta herramienta de wolfram es perfecta para resolver una amplia gama de ecuaciones matemáticas, desde ecuaciones lineales simples hasta ecuaciones diferenciales complejas."
                 "Para utilizar la herramienta, debe proporcionar solamente el parámetro ['query'] y este tiene que ser en ingles."
                 "Cualquier resultado debe tener maximo 3 decimales."

    )

    def _run(self, query: Optional[Union[int, float ,str]] = None):
            wolfram = WolframAlphaAPIWrapper(wolfram_alpha_appid="66P22L-GWYUKJYQ6G")
            wolframFinal=wolfram.run(query)
            return wolframFinal

    
        
    def _arun(self, query: str):
        raise Exception('Invalid async tool: {}'.format(query)) from None