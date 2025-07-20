import socket
import threading
import os
import logging
import struct

def get_host():
    try:
        ip = os.popen("hostname -I").read().split()[0]
        return ip
    except Exception as e:
        print("[!] ERROR for get the ip address : {e}")
        return "127.0.0.1"

BUFFER_SIZE = 4096
port = 8880
host = get_host()

logging.basicConfig(
    filename="proxy.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("proxy.log"), logging.StreamHandler()]
)

def start_proxy(host, port):
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serveur.bind((host, port))
    serveur.listen(100)
    logging.info(f"[@] Start of the proxy on @{host}:{port}")
    while True:
        client_socket, addr = serveur.accept()
        client_ip = addr[0]
        logging.info(f"[+] Connexion from client IP: {client_ip}")
        threading.Thread(target=handle_connection, args=(client_socket, client_ip)).start()

def handle_connection(client_socket, client_ip):
    try:
        peek = client_socket.recv(1, socket.MSG_PEEK)
        if peek == b'\x05':
            handle_socks5(client_socket, client_ip)
        else:
            data = client_socket.recv(BUFFER_SIZE)
            if data.startswith(b'CONNECT'):
                handle_https(client_socket, data, client_ip)
            elif data.startswith(b'OPEN'):
                handle_ftp(client_socket, client_ip)
            elif data.split(b' ')[0] in [b'GET', b'POST', b'HEAD', b'PUT', b'DELETE', b'OPTIONS', b'PATCH']:
                handle_http(client_socket, data, client_ip)
            else:
                logging.warning(f"[!] Unknown protocol from {client_ip}, closing connection")
                client_socket.close()
    except Exception as e:
        logging.error(f"[!] CONNECTION ERROR from {client_ip}: {e}")
        client_socket.close()

def handle_socks5(client, client_ip):
    try:
        client.recv(2)
        client.recv(1)
        client.sendall(b'\x05\x00')

        request = client.recv(4)
        ver, cmd, _, atyp = request[0], request[1], request[2], request[3]

        if atyp == 1:
            addr = socket.inet_ntoa(client.recv(4))
        elif atyp == 3:
            domain_len = client.recv(1)[0]
            addr = client.recv(domain_len).decode()
        elif atyp == 4:
            addr = socket.inet_ntop(socket.AF_INET6, client.recv(16))
        else:
            logging.warning(f"[!] Unknown address from {client_ip}, closing connection")
            client.close()
            return
        port = struct.unpack('!H', client.recv(2))[0]

        logging.info(f"[*] SOCKS5 tunnel requested by {client_ip} to {addr}:{port}")
        remote = socket.create_connection((addr, port))
        client.sendall(b'\x05\x00\x00\x01' + b'\x00' * 6)
        
        pipe(client, remote)
    except Exception as e:
        logging.error(f"[!] SOCKS5 ERROR from {client_ip}: {e}")
        client.close()

def handle_http(client, data, client_ip):
    try:
        request = data.decode(errors="ignore")
        if not request:
            client.close()
            return

        lines = request.split("\r\n")
        host = None
        for line in lines:
            if line.lower().startswith("Host:"):
                host = line.split(":", 1)[1].strip()
                break
        
        if not host:
            logging.warning(f"[!] no host for the HTTP request from : {client_ip}")
            client.close()
            return
        
        if ":" in host:
            host, port = host.split(":")
            port = int(port)
        else:
            port = 80

        logging.info(f"[*] HTTP tunnel requested by {client_ip} to {host}:{port}")

        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect((host, port))

        remote.sendall(data)
        
        pipe(client, remote)
    except Exception as e:
        logging.error(f"[!] HTTP ERROR from {client_ip}: {e}")
        client.close()
                
def handle_https(client, data, client_ip):
    try:
        while b"\r\n\r\n" not in data:
            more = client.recv(BUFFER_SIZE)
            if not more:
                raise Exception("Client closed connection before sending full request")
            data += more

        line = data.decode().split("\n")[0]
        addr = line.split()[1]
        host, port = addr.split(":")
        port = int(port)

        logging.info(f"[*] HTTPS tunnel requested by {client_ip} to {host}:{port}")
        remote = socket.create_connection((host, port))
        client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

        pipe(client, remote)
    except Exception as e:
        logging.error(f"[!] HTTPS ERROR from {client_ip}: {e}")
        client.close()

def handle_ftp(client_socket, client_ip):
    try:
        data = client_socket.recv(BUFFER_SIZE).decode(errors="ignore").strip()
        if not data.startswith("[*] OPEN") and not data.startswith("OPEN"):
            client_socket.sendall(b"500 Unknown command")
            client_socket.close()
            return
        if data.startswith("[*] OPEN"):
            target = data.split("OPEN", 1)[1].decode(errors="ignore")
        else:
            target = data.split("OPEN", 1)[1].decode(errors="ignore")

        if ":" in target:
            ip, port = target.split(":")
        else:
            ip, port = target.split()
        ip = ip.strip()
        port = int(port.strip())

        ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ftp_socket.connect((ip, port))

        logging.info(f"[*] FTP tunnel requested by {client_ip} to {ip}:{port}")

        banner = ftp_socket.recv(BUFFER_SIZE)
        client_socket.sendall(banner)
        
        pipe(client_socket, ftp_socket)
    except Exception as e:
        logging.error(f"[!] FTP ERROR from {client_ip}: {e}")
        try:
            client_socket.sendall(b"500 FTP Proxy Error")
        except:
            pass
        client_socket.close()

def pipe(sock1, sock2):
    def forward(src, dst):
        try:
            while True:
                data = src.recv(BUFFER_SIZE)
                if not data:
                    print("[!] ERROR from data")
                    break
                dst.sendall(data)
        except Exception as e:
            print(f"[!] PIPE ERROR : {e}")
        finally:
            try:
                src.shutdown(socket.SHUT_RD)
            except:
                pass
            try:
                dst.shutdown(socket.SHUT_WR)
            except:
                pass
            src.close()
            dst.close()
    threading.Thread(target=forward, args=(sock1, sock2)).start()
    threading.Thread(target=forward, args=(sock2, sock1)).start()

if __name__ == "__main__":
    start_proxy(host, port)
