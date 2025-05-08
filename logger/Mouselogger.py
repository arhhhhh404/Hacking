from pynput.mouse import Listener
import logging

print("---------------------------------|welcome to Mouselogger|---------------------------------")
logging.basicConfig(filename='Mouse.txt', level=logging.DEBUG, format="%(asctime)s: %(message)s")

def on_move(x, y):
    logging.debug(f"la souris se trouve en position: ({x}, {y})")

def on_click(x, y, button, pressed):
    if pressed:
        logging.debug(f"Clic détecté à la position ({x}, {y}) avec le bouton {button}")
    else:
        logging.debug(f"Clic relâché à la position ({x}, {y}) avec le bouton {button}")

def on_scroll(x, y, dx, dy):
    logging.debug(f"Défilement à la position ({x}, {y}) avec dx={dx}, dy={dy}")

with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as l:
    l.join()