import socket
import argparse
import threading


parser = argparse.ArgumentParser(description="Scanner de ports simple en multithread.")
parser.add_argument("-t", "--target", dest="target_ip", required=True, help="Adresse IP de la cible")
parser.add_argument("-p", "--ports", dest="target_ports", required=True, help="Liste de ports à scanner")

args = parser.parse_args()

ip = args.target_ip
ports = args.target_ports.split(",")

def scan_port(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((ip, port))
        if result == 0:
            print(f"    - [+] Le port {port} est ouvert")
        else:
            print(f"    - [-] Le port {port} est fermé")
    except Exception as err:
        print(f"    - [!] Erreur : {err}")
    finally:
        s.close()

for port in ports:
    try:
        port = int(port)
        t = threading.Thread(target=scan_port, args=(ip, port))
        t.start()
    except ValueError:
        print(f"[!] Port invalide : {port}")