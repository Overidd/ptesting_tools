from scapy import all as scapy
# from termcolor import colored
import argparse
import sys

def arguments():
   parse = argparse.ArgumentParser(description='Escaner de ips con ICMP')
   parse.add_argument('-t','--target', dest='target', help='Rango de ips a escanear: (ej: 192.168.1.0/24 or 192.168.1.1)')

   args = parse.parse_args()
   if args.target is None:
      parse.print_help()
      sys.exit(0)
      
   return args.target

def scanner_arp(target):
   broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff") # Capa ethernet
   arp_request = scapy.ARP(pdst=target) # Capa ARP encapsulado en la capa ethernet
   packet = broadcast/arp_request # Construimos el paquete ARP, uniendo las capas, usando el operador de conposicion
   answered,unanswered = scapy.srp(packet, timeout=2, verbose=False)
   
   resultado = answered.summary()
   if resultado:
      print(f'[+] Hosts activos en el rango {target}')
      print(resultado)
      

def main():
   target_str = arguments()
   scanner_arp(target_str)

if __name__ == '__main__':
   main()