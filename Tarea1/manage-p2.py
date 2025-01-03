#!/usr/bin/env python

import sys
import json
import subprocess
from lxml import etree
from lib_vm import VM, NET
import logging, sys


# Creacion y configuracion del logger
def init_log(debug_mode):
    logging.basicConfig(level=logging.DEBUG if debug_mode else logging.INFO)
    log = logging.getLogger('auto_p2')
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.propagate = False
    return log

#Pausa
def pause():
    programPause = input("-- Press <ENTER> to continue...")


#Leer archivo de configuración manage-p2.json
#Devuelve el objeto json
def read_config():
    try:
        with open("manage-p2.json") as archivo:
            config = json.load(archivo)
            print("Configuración leída:")
            if "number_of_servers" in config:
                if config['number_of_servers'] in range(1, 6):
                    return config
                else:
                    print("El número de servidores debe estar entre 1 y 5")
                    return None
            return config
    except FileNotFoundError:
        print("No se encontró el archivo de configuración manage-p2.json")
        return None
    except json.JSONDecodeError:
        print("Error al leer el archivo de configuración manage-p2.json")
        return None

#Inicializa las máquinas virtuales
#Devuelve una lista con las máquinas virtuales.
def initialize_vms(num_servers, log):
    log.debug("Inicializando máquinas virtuales...")
    mvs = []
    for i in range(num_servers):
        mvs.append(VM(f"s{i+1}"))  # Servidores s1, s2, ...
    mvs.append(VM("lb"))  # Balanceador
    mvs.append(VM("c1"))  # Cliente
    return mvs



def create(config, log, mvs, net):
    log.info("Función 'create' invocada: Inicializando máquinas virtuales...")
    
    #mv.create_vm(base_image, interfaces)
    #  - Crea imágenes
    # - Crea definiciones XML
    # - Configura la imagen        
    
    for mv in mvs:
        if mv.name == "lb":
            interfaces = [
                {"addr": "10.1.1.1", "mask": "255.255.255.0"},  # eth0
                {"addr": "10.1.2.1", "mask": "255.255.255.0"}   # eth1
        ]
        elif mv.name == "c1":
            interfaces = [{"addr": "10.1.1.2", "mask": "255.255.255.0"}]
        else:
            i = mv.name[-1]
            interfaces = [{"addr": f"10.1.2.1{i}", "mask": "255.255.255.0"}]
        mv.create_vm(f"{mv.name}.qcow2", interfaces)
    net.create_net()
    log.info("Máquinas virtuales creadas correctamente")


def start(config, log, mvs, net):
    log.info("Función 'start' invocada: Arrancando máquinas virtuales...")
    for mv in mvs:
        mv.start_vm()
    log.info("Todas las máquinas virtuales han sido arrancadas correctamente.")

def stop(config, log, mvs, net):
    log.info("Función 'stop' invocada: Parando máquinas virtuales...")
    for mv in mvs:
        mv.stop_vm()
    log.info("Todas las máquinas virtuales han sido paradas correctamente.")

def destroy(config, log, mvs, net):
    log.info("Función 'destroy' invocada: Destruyendo máquinas virtuales y redes")
    
    for mv in mvs:
        mv.destroy_vm()

    net.destroy_net()
    log.info("Máquinas virtuales y redes destruidas correctamente.")



def main():

    # Validar que se pasa un argumento
    if len(sys.argv) < 2:
        print("Uso: python3 manage_p2.py <orden>")
        print("Opciones válidas: create, start, stop, destroy")
        sys.exit(1)
    
    # Leer el argumento
    command = sys.argv[1]
    
    # Diccionario para mapear comandos a funciones
    commands = {
        "create": create,
        "start": start,
        "stop": stop,
        "destroy": destroy
    }

    #Leer archivo de configuración manage-p2.json
    config = read_config()

    if config is None:
        print("Error al leer archivo de configuración")
        sys.exit(1)

    #Configurar logging
    debug_mode = config.get("debug", False)
    log = init_log(debug_mode)
    #Nº de servidores (por defecto 3) 
    num_servers = config.get("number_of_servers", 3)
    log.debug(f"Inicializado número de servidores: {num_servers}")
    #Inicializa array de MVs 
    mvs = initialize_vms(num_servers, log)
    #Inicializa redes
    net = NET("host")
    

    # Verificar si el comando es válido e invocar la función correspondiente
    # HAY QUE PASAR CONFIG A QUIEN LO NECESITE

    if len(sys.argv) < 2:
        print("Uso: python3 manage_p2.py <orden>")
        print("Opciones válidas: create, start, stop, destroy")
        sys.exit(1)

    command = sys.argv[1]

    if command in commands:
        if len(sys.argv) > 2 and sys.argv[2]:
            vm_name = sys.argv[2]
            for mv in mvs:
                if mv.name == vm_name:
                    if command == "start":
                        mv.start_vm()
                    elif command == "stop":                       
                        mv.stop_vm()
                    elif command == "console":
                        mv.show_console_vm()
                    break
            else:
                print(f"Máquina virtual no encontrada: {vm_name}")
        else:
            commands[command](config, log, mvs, net)  # Invocar la función asociada
    else:
        print(f"Comando desconocido: {command}")
        print("Opciones válidas: create, start, stop, destroy")
        sys.exit(1)

if __name__ == "__main__":
    main()
