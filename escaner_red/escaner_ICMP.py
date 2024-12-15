from concurrent.futures import ThreadPoolExecutor
from termcolor import colored
import subprocess
import argparse
import signal
import sys

def def_handler(sig, frame):
   print(colored("\n[!] Saliendo...","red"))
   sys.exit(0)

signal.signal(signal.SIGINT, def_handler)

def arguments() -> str:
   parse = argparse.ArgumentParser(description='Escaner de ips con ICMP')
   parse.add_argument('-t', '--target', help='Rango de ips a escanear: (ej: 192.168.1.1-255)')
   args = parse.parse_args()
   if args.target is None:
      parse.print_help()
      sys.exit(0)
      
   return args.target

def parse_target(target:str) -> list:
   target_list = target.split('.')
   target_three_octets = '.'.join(target_list[:3]) 

   if len(target_list) != 4:
      print(colored("[!] Rango de ips incorrecto, -h para mas informacion","red"))
      sys.exit(0)
      return
   
   if '-' in target_list[3]:
      start, end = target_list[3].split('-')
      return [f'{target_three_octets}.{i}' for i in range(int(start), int(end)+1)]

   return [target]

def scan_host(target):
   try:
      ping = subprocess.run(['ping', '-c', '1', '-W', '1', target], timeout=2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

      if ping.returncode == 0:
         print(colored(f'[+] La ip {target} esta activa', 'green'))

   except subprocess.TimeoutExpired:
      pass

def loop_scan_host(targets):
   with ThreadPoolExecutor(max_workers=100) as executor:
      executor.map(scan_host, targets)

def main():
   target_str = arguments()
   targets = parse_target(target_str)

   print(colored(f'[+] Iniciando escaneo de los hosts en el rango {target_str}', 'yellow'))
   loop_scan_host(targets)
   print(colored(f'[+] Escaneo finalizado', 'yellow'))

if __name__ == '__main__':
   main()