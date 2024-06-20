import asyncio
from pyscript import document, display, fetch
from pyodide.ffi.wrappers import add_event_listener
from PY.LIBRARY.domdict import DOMDict
from bs4 import BeautifulSoup
from re import split
from random import choice
import requests

class App:
    dizModel = {}
    dom = {}
    dizControl = {}

def init_app_Model():
    dizModel = {
        "base_url": "http://0.0.0.0",
        "port": "8000",
        "folder": "AUDIO",
        "extension": "mp3",
        "generate_playlist": [],
        "current_index": 0,
        "composed_playlist": [],
        "button_background_played": "#8BC34A",
        "button_ids_played": []
    }
    return dizModel

def init_app_Control():
    dizCallback = {
        "cb_generate": callback_generate,
        "cb_next": callback_next,
        "cb_button_click": callback_button_click,
        "cb_composed_playlist": callback_composed_playlist
    }
    return dizCallback

def init_binding():
    add_event_listener(App.dom["generate_playlist"], "click", App.dizControl["cb_generate"])
    add_event_listener(App.dom["audio_player"], "timeupdate", App.dizControl["cb_next"])
    add_event_listener(App.dom["composed_playlist"], "click", App.dizControl["cb_composed_playlist"])

def listFD():
    url = build_base_url()
    extension = App.dizModel["extension"]
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    return [url + '/' + node.get("href") for node in soup.find_all('a') if node.get("href").endswith(extension)]

def build_base_url():
    base_url = App.dizModel["base_url"]
    port = App.dizModel["port"]
    folder = App.dizModel["folder"]
    return f"{base_url}:{port}/{folder}"

def build_uri(filename):
    url = build_base_url()
    return f"{url}/{filename}"

def build_filename(column, row, value, extension):
    return f"M-{column:02d}-{row:02d}-{value:03d}.{extension}"

def from_uri_to_matrix_index(uri):
    file_name = split("/", uri).pop()
    sub_elements = split("\.|-", file_name)
    column = int(sub_elements[1])
    row = int(sub_elements[2])
    value = int(sub_elements[3])
    return column, row, value

def static_matrix():
    elements = App.dizModel["files"]
    matrix = {}
    for uri in elements:
        column, row, value = from_uri_to_matrix_index(uri)
        if column not in matrix:
            matrix[column] = {}
        matrix[column][row] = value
    display(f"Matrice statica: {matrix}")
    return matrix

def matrix_files():
    matrix = App.dizModel["matrix_cols_rows"]
    extension = App.dizModel["extension"]
    matrix_filenames = {}
    for column in matrix:
        for row in matrix[column]:
            value = matrix[column][row]
            filename = build_filename(column, row, value, extension)
            if column not in matrix_filenames:
                matrix_filenames[column] = {}
            matrix_filenames[column][row] = filename
    display(f"Matrice dei files: {matrix_filenames}")
    return matrix_filenames

def generate_sequence():
    list_sequence = []
    columns = sorted(App.dizModel["matrix_filenames"].keys())
    for column in columns:
        rows = list(sorted(App.dizModel["matrix_filenames"][column]))
        row = choice(rows)
        value = App.dizModel["matrix_filenames"][column][row]
        filename = build_uri(value)
        list_sequence.append(filename)
    return list_sequence

def callback_generate(event=None):
    sequence = generate_sequence()
    App.dizModel["generate_playlist"] = sequence
    App.dizModel["current_index"] = 0
    display(f"Playlist generata: {sequence}")
    play()

def play():
    dom_filename = App.dom["filename"]
    sequence = App.dizModel["generate_playlist"]
    index = App.dizModel["current_index"]
    if index < len(sequence):
        mp3_file = sequence[index]
        audio = App.dom["audio_player"]
        audio.src = mp3_file
        dom_filename.innerHTML = f"Sto suonando: {mp3_file}"
        column, row, value = from_uri_to_matrix_index(mp3_file)
        id_button = f"M-{column:02d}-{row:02d}"
        button = App.dom[id_button]
        button.style.background = App.dizModel["button_background_played"]
        App.dizModel["button_ids_played"].append(id_button)
        audio.play()
    else:
        for id_button in App.dizModel["button_ids_played"]:
            button = App.dom[id_button]
            button.style.background = App.dizModel["button_background_default"]
        dom_filename.innerHTML = "Playlist terminata"

def callback_next(event=None):
    audio = App.dom["audio_player"]
    if audio.currentTime > 1.61:
        App.dizModel["current_index"] += 1
        play()

def callback_button_click(event):
    button = event.currentTarget
    filename = button.value
    App.dizModel["composed_playlist"].append(filename)
    display(f"File aggiunto alla playlist: {filename}")

def callback_composed_playlist(event=None):
    App.dizModel["generate_playlist"] = App.dizModel["composed_playlist"]
    App.dizModel["current_index"] = 0
    display(f"Playlist composta: {App.dizModel['generate_playlist']}")
    play()

def create_button_matrix():
    button_container = App.dom["button_container"]

    for i in range(1, 16 + 1):
        td_element = document.createElement("td")
        td_element.id = i
        for j in range(1, 11 + 1):
            tr_element = document.createElement("tr")
            tr_element.id = j
            button = document.createElement("button")
            button.id = f"M-{i:02d}-{j:02d}"
            button.innerHTML = "XXX"
            tr_element.appendChild(button)
            td_element.appendChild(tr_element)
            button_container.appendChild(td_element)

def associate_files_to_buttons():
    matrix_filenames = App.dizModel["matrix_filenames"]

    for column in matrix_filenames:
        for row in matrix_filenames[column]:
            value = App.dizModel["matrix_cols_rows"][column][row]
            filename = matrix_filenames[column][row]
            id_button = f"M-{column:02d}-{row:02d}"
            button = App.dom[id_button]
            button.innerHTML = f"{value:03d}"
            button.value = build_uri(filename)
            add_event_listener(button, "click", App.dizControl["cb_button_click"])

async def load_all_mp3_files():
    urls = App.dizModel["files"]
    for url in urls:
        response = await fetch(url)
        if response.ok:
            display(f"Precaricato: {url}")
        else:
            display(f"Errore nel precaricare: {url}")

def main():
    App.dizModel = init_app_Model()
    App.dizModel["files"] = listFD()
    App.dizModel["matrix_cols_rows"] = static_matrix()
    App.dizModel["matrix_filenames"] = matrix_files()
    App.dom = DOMDict()
    App.dizModel["button_background_default"] = App.dom["generate_playlist"].style.background
    App.dizControl = init_app_Control()
    init_binding()
    create_button_matrix()
    associate_files_to_buttons()
    asyncio.gather(load_all_mp3_files())

if __name__ == "__main__":
    main()
