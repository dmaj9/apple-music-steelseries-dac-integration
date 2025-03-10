import os
import sys
import msvcrt
import tempfile

lockfile = os.path.join(tempfile.gettempdir(), 'dac_app.lock')

def single_instance():
    global lockfile
    try:
        fp = open(lockfile, 'w')
        msvcrt.locking(fp.fileno(), msvcrt.LK_NBLCK, 1)
        return fp
    except IOError:
        sys.exit(0)

# Bloquear instancias duplicadas
lock_fp = single_instance()

import requests
import time
from pywinauto import Desktop
import json

def get_gamesense_address():
    core_props_path = os.path.expandvars(r'%PROGRAMDATA%\SteelSeries\SteelSeries Engine 3\coreProps.json')
    try:
        with open(core_props_path, 'r') as f:
            data = json.load(f)
        return "http://" + data['address']
    except Exception as e:
        print("[Error leyendo coreProps.json]:", e)
        return None



# Dirección que obtuviste desde coreProps.json
GAMESENSE_ADDRESS = get_gamesense_address()

# App personalizada
GAME_NAME = "MUSIC"
GAME_DISPLAY_NAME = "Music Player"
DEVELOPER_NAME = "David Castillo"

# Duraciones
SHOW_SONG_SECONDS = 4  # Mostrar canción
SHOW_DEFAULT_SECONDS = .5  # Pantalla predeterminada

# Scroll
SCROLL_STEP_DELAY = .2  # Velocidad del scroll (0.1 seg por paso)
MAX_DISPLAY_LENGTH = 18  # Caracteres visibles (ajustable según pantalla DAC)


def register_game():
    payload = {
        "game": GAME_NAME,
        "game_display_name": GAME_DISPLAY_NAME,
        "developer": DEVELOPER_NAME,
        "deinitialize_timer_length_ms": 0
    }
    try:
        requests.post(f"{GAMESENSE_ADDRESS}/game_metadata", json=payload, timeout=3)
    except requests.RequestException:
        pass  

def register_handler():
    handler_payload = {
        "game": GAME_NAME,
        "event": "SONG_INFO",
        "icon_id": 0,
        "min_value": 0,
        "max_value": 100,
        "value_optional": True,
        "handlers": [
            {
                "device-type": "screened",
                "zone": "one",
                "mode": "screen",
                "datas": [
                    {
                        "lines": [
                            {
                                "has-text": True,
                                "context-frame-key": "text"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    try:
        requests.post(f"{GAMESENSE_ADDRESS}/bind_game_event", json=handler_payload, timeout=3)
    except requests.RequestException:
        pass  


def send_song_info(text):
    event_payload = {
        "game": GAME_NAME,
        "event": "SONG_INFO",
        "data": {
            "value": 0,
            "frame": {
                "text": text
            }
        }
    }
    try:
        requests.post(f"{GAMESENSE_ADDRESS}/game_event", json=event_payload, timeout=3)
    except requests.RequestException:
        pass 


def stop_game():
    payload = {"game": GAME_NAME}
    try:
        requests.post(f"{GAMESENSE_ADDRESS}/stop_game", json=payload, timeout=3)
    except requests.RequestException:
        pass  


def get_current_song(retries=3, delay=0.5):
    for _ in range(retries):
        try:
            app = Desktop(backend='uia').window(title_re=".*Music.*")
            panes = app.descendants(control_type="Pane")
            filtered_panes = [pane for pane in panes if pane.element_info.automation_id == "myScrollViewer"]

            if len(filtered_panes) < 2:
                time.sleep(delay)
                continue

            song_pane = filtered_panes[0]
            artist_pane = filtered_panes[1]

            song_texts = song_pane.descendants(control_type="Text")
            song_name = song_texts[0].window_text() if song_texts else None

            artist_full = artist_pane.element_info.name
            artist_name = artist_full.split(" — ")[0] if " — " in artist_full else artist_full

            if song_name and artist_name:
                return song_name, artist_name
        except:
            time.sleep(delay)
    return None, None


def scroll_text(full_text, display_time):
    text = f"🎵 {full_text} "
    if len(text) <= MAX_DISPLAY_LENGTH:
        send_song_info(text)
        time.sleep(display_time)
    else:
        text += " " * MAX_DISPLAY_LENGTH
        end_time = time.time() + display_time
        while time.time() < end_time:
            for i in range(len(text) - MAX_DISPLAY_LENGTH + 1):
                part = text[i:i + MAX_DISPLAY_LENGTH]
                send_song_info(part)
                time.sleep(SCROLL_STEP_DELAY)
                if time.time() >= end_time:
                    break


if __name__ == "__main__":
    register_game()
    time.sleep(1)
    register_handler()

    last_song = None
    last_artist = None

    while True:
        song, artist = get_current_song()

        if song and artist and (song != last_song or artist != last_artist):
            last_song = song
            last_artist = artist

        if last_song and last_artist:
            scroll_text(f"{last_song} - {last_artist}", SHOW_SONG_SECONDS)

        stop_game()
        time.sleep(SHOW_DEFAULT_SECONDS)
