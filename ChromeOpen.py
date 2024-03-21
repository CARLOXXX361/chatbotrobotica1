from subprocess import call
from langchain.tools import BaseTool

class ChromeOpen(BaseTool):
    name = "open_Chrome"
    description = "Abre chrome con la url que el usuario indica y solo respondes 'Pestaña Abierta.' "

    def _run(self, url: str):
            link = "" if url is None else url
            call("C:/Program Files/Google/Chrome/Application/chrome.exe " + link)
            msg= "Debes responder lo siguiente y solamente eso: 'Pestaña Abierta.'"
            return msg
    def _arun(self, query: str):
            pass
