from pyscript import document, display
from js import Audio
from pyodide.ffi.wrappers import add_event_listener
from PY.LIBRARY.domdict import DOMDict
from bs4 import BeautifulSoup
from re import split
import requests

class App:
    dizModel = {}
    dom = {}
    dizControl = {}

def init_app_Model():
    dizModel = {"files": listFD("http://0.0.0.0:8000/AUDIO")
    }
    return dizModel


def init_app_Control():
    dizCallback = {
        'cb_tst01': callback_tst01
    }
    return dizCallback


def init_binding():
    add_event_listener(App.dom["tst01"], "click", App.dizControl['cb_tst01'])

def listFD(url):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(".mp3")]


def option_elements(file_names):
    select_element = App.dom["canzoni"]
    i = 0
    for file_name in file_names:
        option_element = document.createElement("option")
        option_element.value = file_name
        option_element.innerHTML = split("/", file_name).pop()
        select_element.appendChild(option_element)
    display(f"Ho caricato tutti gli elementi")
def callback_tst01(event=None):
    dom_select = App.dom["canzoni"]
    mp3_file = dom_select.value
    display(mp3_file)
    dom_tst01 = App.dom["tst01"]

    dom_PLAY = App.dom["FILE"]

    dom_PLAY.innerHTML = f"{mp3_file}"
    file = Audio.new(mp3_file)
    file.load()
    file.play()
    dom_tst01.innerHTML = "STOP"
def main():
    App.dizModel = init_app_Model()
    App.dom = DOMDict()
    App.dizControl = init_app_Control()
    init_binding()
    option_elements(App.dizModel["files"])

if __name__ == "__main__":
    main()
