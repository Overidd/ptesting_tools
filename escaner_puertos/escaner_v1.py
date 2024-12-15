import socket
import argparse
import sys
from termcolor import colored
from typing import Union, List, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import signal


def def_handler(sig, frame):
   print(colored("Saliendo del escaneo...", "red"))
   for s in open_sockets:
      s.close()
   sys.exit(1)

open_sockets = []
signal.signal(signal.SIGINT, def_handler)

def get_args():
   parser = argparse.ArgumentParser(description="Escaneador de puertos")
   parser.add_argument('-t','--target', dest='target' ,help='Direccion a escanear: (Ej: 192.168.1.1)')
   parser.add_argument('-p', '--port', dest='port' ,help='Puerto a escanear: (Ej: 80, 443), (1-1000), (80)',)
   opcions = parser.parse_args()

   if opcions.target is None or opcions.port is None:
      parser.print_help()
      sys.exit(1)

   return opcions.target, opcions.port

def create_socket() -> socket.socket:
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   open_sockets.append(s)
   return s

def send_request(s, host, method="HEAD") -> Union[str, None]:
   try:
      s.sendall(f"{method} / HTTP/1.0\r\nHost: {host}\r\n\r\n".encode())
      response = s.recv(4096)
      header = response.decode('utf-8', errors='ignore').split('\r\n')[0]
      return header
      
   except Exception:
      return None

def port_scan(host, port):
   try: 
      with create_socket() as s:
         s.settimeout(3)
         s.connect((host, port))
            
         # Intentar obtener la cabecera HTTP si aplica)
         s.sendall(b'HEAD / HTTP/1.0\r\n\r\n')
         response = s.recv(4096)
         header = response.decode('utf-8', errors='ignore').split('\r\n')[0]

         if header.strip():
            print(colored(f'El puerto {port} está abierto, respuesta:{header}', 'green'))
         else:
            print(colored(f'El puerto {port} está abierto pero no envió cabecera. Intentando de nuevo...', 'blue'))
            
            header_new = send_request(s, host, method="GET")
            if header_new.strip():
                print(colored(f'El puerto {port} respondió con GET: {header}', 'green'))
            else:
                print(colored(f'El puerto {port} está abierto pero no envió respuesta válida.', 'yellow'))


   except socket.timeout:
      print(colored(f'El puerto {port} está abierto pero no responde (timeout).', 'yellow'))
   except ConnectionResetError:
      print(colored(f'El puerto {port} rechazó la conexión.', 'red'))
   except Exception as e:
        pass


def parse_ports(ports_str) -> Union[List[int], Tuple[int,]]:
    try:
        if ',' in ports_str:
            ports = list(map(int, ports_str.split(',')))
        elif '-' in ports_str:
            start, end = map(int, ports_str.split('-'))
            ports = list(range(start, end + 1))
        else:
            ports = [int(ports_str)]

        # Validar que los puertos estén en el rango permitido
        if any(port < 1 or port > 65535 for port in ports):
            raise ValueError("Rango de puertos no válido. Deben estar entre 1 y 65535.")
        return tuple(ports)
    except ValueError as e:
        print(colored(f"Error: {e}", "red"))
        sys.exit(1)

def loop_scan_ports(host, ports):
   initial_time = time.time()
   print('Iniciando escaneo: 0 segundos')
   with ThreadPoolExecutor(max_workers=50) as executor:
      executor.map(lambda port: port_scan(host, port), ports)
   print(f'Escaneo finalizado: {round(time.time() - initial_time, 2)} segundos')


def loop_scan_ports2(host, ports):
   max_threads = 50
   semaphore = threading.Semaphore(max_threads)  # Limita el número de hilos simultáneos

   def thread_target(host, port):
      with semaphore:  # Adquiere el semáforo
         port_scan(host, port)  # Ejecuta la función objetivo

   threadings = []
   initial_time = time.time()
   print('Iniciando escaneo: 0 segundos')
   for port in ports:
      hilo = threading.Thread(target=thread_target, args=(host, port))
      threadings.append(hilo)
      hilo.start()

   for hilo in threadings:
      hilo.join()

   print(f'Escaneo finalizado: {round(time.time() - initial_time, 2)} segundos')

def main():
   host, ports_str  = get_args()
   posts = parse_ports(ports_str)
   loop_scan_ports(host, posts)

if __name__ == '__main__':
   main()


