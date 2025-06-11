import requests
import argparse
import os

parser = argparse.ArgumentParser("<-----------------------------| Web Fuzzing SQL |----------------------------->")
parser.add_argument("--url", required=True, help="Base URL (e.g., https://example.com/)")
parser.add_argument("--file", required=True, help="Path to the login wordlist")

args = parser.parse_args()
url = args.url
fichier = args.file

if not os.path.isfile(fichier):
    print(f"[!] Le fichier '{fichier}' n'existe pas.")
    exit(1)

if not url.endswith("/"):
    url += "/"

with open(fichier, "r") as attack:
    for login_page in attack:
        login_page = login_page.strip()
        full_url = url + login_page
        print(f"[?] Checking {full_url}...")
        try:
            response = requests.get(full_url, timeout=5)
            if "mysql" in response.text.lower():
                print(f"[+] Attack detected at: {full_url}")
        except requests.RequestException as e:
            print(f"[!] Error while checking {full_url}: {e}")
