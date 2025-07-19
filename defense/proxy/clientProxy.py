
import socket
import os
import ssl
import argparse
import struct
import re

BUFFER_SIZE = 4096

def use_proxy(mode, proxy_host, proxy_port, target_host, target_port):
    if mode == "socks5":
        socks5_client(proxy_host, proxy_port, target_host, target_port)
    elif mode == "http":
        http_client(proxy_host, proxy_port, target_host)
    elif mode == "https":
        https_client(proxy_host, proxy_port, target_host, target_port)
    elif mode == "ftp":
        ftp_client(proxy_host, proxy_port, target_host, target_port)
    else:
        print("[!] Unknown mode (choose : socks5, http, https, ftp)")

def socks5_client(proxy_host, proxy_port, target_host, target_port):
    print(f"[*] Connexion SOCKS5 from : {proxy_host}:{proxy_port} to {target_host}:{target_port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((proxy_host, proxy_port))

    sock.sendall(b'\x05\x01\x00')
    if sock.recv(2) != b'\x05\x00':
        print("[!] auth SOCKS5 not accepted")
        sock.close()
        return

    try:
        addr = socket.inet_aton(socket.gethostbyname(target_host))
        request = b'\x05\x01\x00\x01' + addr + struct.pack('>H', target_port)
    except socket.gaierror:
        host_bytes = target_host.encode()
        request = b'\x05\x01\x00\x03' + bytes([len(host_bytes)]) + host_bytes + struct.pack('>H', target_port)

    sock.sendall(request)
    resp = sock.recv(10)
    if resp[1] != 0x00:
        print(f"[!] ERROR SOCKS5 : {resp[1]}")
        sock.close()
        return
    print("[+] SOCKS5 tunnel etablished")

    try:
        while True:
            print("[?] What do you want to do ?")
            print("1. Text chain (UTF-8)")
            print("2. Hexadecimal data")
            print("3. Quit")
            choice = input("[>>]").strip()
            if choice == "1":
                data = input("[>] Text to send : ")
                sock.sendall(data.encode())
            elif choice == "2":
                hexdata = input("[>] Hexadecimal data to send : ").strip().replace(" ", "")
                try:
                    binary = bytes.fromhex(hexdata)
                    sock.sendall(binary)
                except ValueError:
                    print("[!] Invalid hex format")
                    continue
            elif choice == "3":
                break
            else:
                print("[!] Invalid choice")
                continue
            
            print("[*] Wait for response...")
            try:
                sock.settimeout(2)
                response = sock.recv(BUFFER_SIZE)
                if response:
                    try:
                        print(f"[<] response :\n{response.decode(errors='ignore')}")
                    except UnicodeDecodeError:
                        print(f"[<] binary response : {response.hex()}")
                else:
                    print("[!] No data receive")
            except socket.timeout:
                print("[!] No response")
            sock.settimeout(None)         
    except KeyboardInterrupt:
        print("[!] Closing")

    sock.close()

def http_client(proxy_host, proxy_port, target_host):
    print(f"[*] Connexion HTTP from : {proxy_host}:{proxy_port} to {target_host}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((proxy_host, proxy_port))

    methods = ["GET", "POST", "HEAD", "PUT", "DELETE", "OPTIONS", "PATCH"]
    try:
        choice = int(input(f"[?] choose your HTTP method :\n" + f"\n".join([f"{i+1} {m}" for i, m in enumerate(methods)]) + "\n")) -1
        method = methods[choice]
    except (ValueError, IndexError):
        print("[!] Invalid choice")
        sock.close()
        return

    path = input("[?] Enter the path (by default '/') : ") or "/"
    body = ""
    if method in ["POST", "PUT", "PATCH"]:
        body = input("[?] Enter the data to send : ")
        content_type = input("[?] Enter the type of the content : ")
        content_length = len(body.encode())
        request = f"{method} {path} HTTP/1.1\r\nHost: {target_host}\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n{body}"
    else:
        request = f"{method} {path} HTTP/1.1\r\nHost: {target_host}\r\nConnection: close\r\n\r\n"

    sock.sendall(request.encode())
    print(f"[*] Request send to the proxy : {proxy_host}")

    response = b""
    while True:
        data = sock.recv(BUFFER_SIZE)
        if not data:
            break
        response += data

    print(f"[*] Answer from the proxy server :\n {response.decode(errors="ignore")}")
    sock.close() 

def https_client(proxy_host, proxy_port, target_host, target_port):
    print(f"[*] Connexion HTTPS from : {proxy_host}:{proxy_port} to {target_host}:{target_port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((proxy_host, proxy_port))

    request = f"CONNECT {target_host}:{target_port} HTTP/1.1\r\nHost: {target_host}\r\n\r\n"
    sock.sendall(request.encode())

    resp = b""
    while b"\r\n\r\n" not in resp:
        data = sock.recv(BUFFER_SIZE)
        if not data:
            print("[!] No response from proxy")
            sock.close()
            return
        resp += data
        
    if b"200 Connection Established" not in resp:
        print(f"[!] ERROR HTTPS : {resp.decode(errors='ignore')}")
        sock.close()
        return

    print("[+] HTTPS tunnel etablished")

    context = ssl.create_default_context()
    tls_sock = context.wrap_socket(sock, server_hostname=target_host)

    methods = ["GET", "POST", "HEAD", "PUT", "DELETE", "OPTIONS", "PATCH"]
    try:
        choice = int(input(f"[?] choose your HTTP method :\n" + f"\n".join([f"{i+1} {m}" for i, m in enumerate(methods)]) + "\n")) -1
        method = methods[choice]
    except (ValueError, IndexError):
        print("[!] Invalid choice")
        tls_sock.close()
        return

    path = input("[?] Enter the path (by default '/') : ") or "/"
    body = ""
    if method in ["POST", "PUT", "PATCH"]:
        body = input("[?] Enter the data to send : ")
        content_type = input("[?] Enter the type of the content : ")
        content_length = len(body.encode())
        request = f"{method} {path} HTTP/1.1\r\nHost: {target_host}\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n{body}"
    else:
        request = f"{method} {path} HTTP/1.1\r\nHost: {target_host}\r\nConnection: close\r\n\r\n"

    tls_sock.sendall(request.encode())
    print(f"[*] Request send to the server : {target_host}")

    response = b""
    while True:
        data = tls_sock.recv(BUFFER_SIZE)
        if not data:
            break
        response += data

    print(f"[*] Answer from the server :\n {response.decode(errors="ignore")}")
    tls_sock.close()

def ftp_client(proxy_host, proxy_port, target_host, target_port):
    mode = input("[?] FTP mode (active/passive) : ").strip().lower()
    if mode not in ["active", "passive"]:
        print("[!] Invalid FTP mode")
        return
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((proxy_host, proxy_port))
    
    def recv_response(sockeet):
        response = b""
        sockeet.settimeout(2)
        try:
            while True:
                data = sockeet.recv(BUFFER_SIZE)
                if not data:
                    break
                response += data
        except socket.timeout:
            pass
        sockeet.settimeout(None)
        return response.decode(errors="ignore")
        
    sock.sendall(f"[*] OPEN {target_host}:{target_port}".encode())
    print("[ftp<] ", recv_response(sock).strip())

    user = input("[>] USER (username) : ")
    sock.sendall(f"USER {user}\r\n".encode())
    resp1 = recv_response(sock)
    if not resp1.startswith("331"):
        print("[!] User refused")
        return

    password = input("[>] PASS (password) : ")
    sock.sendall(f"PASS {password}\r\n".encode())
    resp2 = recv_response(sock)
    if not resp2.startswith("230"):
        print("[!] Authentification failed")
        return
    
    print(f"[*] logged in with the mode : {mode.upper()}. Type your FTP command (LIST, PWD, RETR...), type exit for quit")
    
    while True:
        cmd = input("[>]").strip()
        if not cmd:
            continue
        if cmd.lower() == "exit":
            sock.sendall(b"QUIT\r\n")
            print("[<] ", recv_response(sock).strip())
            break
                
        needs_data = any(cmd.upper().startswith(x) for x in ["LIST", "NLST", "RETR", "STOR", "APPE", "STOU", "MLSD", "MLST"])

        data_sock = None

        if needs_data:
            data_sock = None
            if mode == "passive":
                sock.sendall(b"PASV\r\n")
                pasv_response = recv_response(sock)

                m = re.search(r"\((\d+,\d+,\d+,\d+,\d+,\d+)\)", pasv_response)
                if not m:
                    print("[!] Failed to parse PASV response")
                    return
                
                parts = list(map(int, m.group(1).split(',')))
                ip = ".".join(map(str, parts[0:4]))
                port = parts[4] * 256 + parts[5]

                data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                data_sock.connect((proxy_host, proxy_port))
                data_sock.sendall(f"OPEN {ip} {port}\r\n".encode())
            elif mode == "active":
                print("[!] Active mode dont fonctionnate on proxy, your not safe !!!")
                data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                data_sock.bind(('', 0))
                data_sock.listen(1)

                ip_local = sock.getsockname()[0]
                port_local = data_sock.getsockname()[1]

                ip_parts = ip_local.split('.')
                p1 = port_local // 256
                p2 = port_local % 256

                port_cmd = f"PORT {','.join(ip_parts)},{p1},{p2}\r\n"
                sock.sendall(port_cmd.encode())
                port_response = recv_response(sock)
                if not port_response.startswith("200"):
                    print("[!] Port command rejected")

                conn, _ = data_sock.accept()
                data_sock = conn

        sock.sendall((cmd + "\r\n").encode())
        print("[<]", recv_response(sock).strip())
    
        if data_sock:
            command_name = cmd.split()[0].upper()
            data = b""

            if command_name in ["STOR", "APPE"]:
                filename = cmd.split(maxsplit=1)[1] if " " in cmd else "download_file"
                if not filename or not os.path.exists(filename):
                    print(f"[!] File '{filename}' not found")
                else:
                    with open(filename, "rb") as f:
                        while True:
                            chunk = f.read(BUFFER_SIZE)
                            if not chunk:
                                break
                            data_sock.sendall(chunk)
            else:
                while True:
                    try:
                        chunk = data_sock.recv(BUFFER_SIZE)
                        if not chunk:
                            break
                        data += chunk
                    except:
                        break
                if cmd.upper().startswith("RETR"):
                    filename = cmd.split(maxsplit=1)[1] if " " in cmd else "download_file"
                    with open(filename, "wb") as f:
                        f.write(data)
                    print(f"[<] File '{filename}' is download")
                else:
                    print("[<] ", data.decode(errors="ignore"))
        data_sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Proxy Client")
    parser.add_argument("mode", choices=["socks5", "http", "https", "ftp"], help="proxy mode to use : socks5 / http / https/ ftp")
    parser.add_argument("proxy_host", help="IP of the proxy serveur")
    parser.add_argument("target_host", help="IP of the target")
    parser.add_argument("target_port", type=int, help="Port of the target")
    
    args = parser.parse_args()
    proxy_port = 8880

    use_proxy(args.mode, args.proxy_host, proxy_port, args.target_host, args.target_port)