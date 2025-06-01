import requests
from bs4 import BeautifulSoup
import argparse

parser = argparse.ArgumentParser("<-----------------------------| Web Scarper |----------------------------->")
parser.add_argument("url", help="URL de la page rechercher")
parser.add_argument("balise", help="Balise HTML à rechercher")
parser.add_argument("class", help="spécificité sur la class", default="")
parser.add_argument("id", help="Spécificité sur le id", default="")

args = parser.parse_args()

try:
    page = requests.get(args.url)
    page.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"[!]: Erreur lors de la requête : {e}")
    exit(1)

soup = BeautifulSoup(page.content, "html.parser")

elements = soup.find_all(args.balise, args.class_ if args.class_ else None, args.id if args.id else None)

for el in elements:
    print(el.get_text(strip=True))