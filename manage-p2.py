#!/usr/bin/env python

import sys
import json
import subprocess
from lxml import etree
from utilidades import create_xml
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

#Numero de mvs
num_vms = 0

#Leer archivo de configuración manage-p2.json
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
    
    num_vms = config["number_of_servers"]
    
    # Crear MVs
    for i in range(num_vms):
        mvs = mvs.append(VM(f"s{i+1}"))
        #create_image(base_image, f"s{i+1}")
    mvs.append(VM("lb"))
    mvs.append(VM("c1"))


# Array de mvs
mvs = []

# Diccionario LAN1
lan1 = [{
    "addr" : "10.1.1.1",
    "mask" : "255.255.255.0"
    }]
lan1.append({
    "addr" : "10.1.1.2",
    "mask" : "255.255.255.0"
    })
lan1.append({
    "addr" : "10.1.1.3",
    "mask" : "255.255.255.0"
    })
# Diccionario LAN2
lan2 = []
for i in range(num_vms):
    lan2.append({
        "addr" : f"10.1.2.1{i+1}",
        "mask" : "255.255.255.0"})



def create(config, log):
    print("Función 'create' invocada: Inicializando máquinas virtuales...")
    base_image = "cdps-vm-base-pc1.qcow2"
    base_xml = "plantilla-vm-pc1.xml"
    
    print(f"Creando escenario con {num_vms} servidores...")
    
    # Crear definiciones XML
    for i in range(num_vms):
        create_xml(base_xml, f"s{i+1}", f"/mnt/tmp/alvaro.pablo/s{i+1}.qcow2", ["LAN2"])
    create_xml(base_xml, "lb", "/mnt/tmp/alvaro.pablo/lb.qcow2", ["LAN1", "LAN2"])
    create_xml(base_xml, "c1", "/mnt/tmp/alvaro.pablo/c1.qcow2", ["LAN1"])
    
    #Creando vms con las definiciones XML
    for mv in mvs:
        if mv.name == "lb":
            mv.create_vm(base_image, ["lan1", "lan2"])
        elif mv.name == "c1":
            mv.create_vm("c1.qcow2", base_image, ["lan1"])
        else:
            mv.create_vm(base_image, ["lan2"])


    # Crear bridges virtuales
    log.debug("Creando bridges virtuales")
    subprocess.run(
            ["sudo", "ovs-vsctl", "add-br", "LAN1"],
            check=True
        )
    subprocess.run(
            ["sudo", "ovs-vsctl", "add-br", "LAN2"],
            check=True
        )


    log.info("Máquinas virtuales definidas correctamente")

#Arranca MVs con "sudo virsh start"

def start(config, log):
    print("Función 'start' invocada: Arrancando máquinas virtuales...")
    for mv in mvs:
        mv.start_vm()
    

def stop(config, log):
    print("Función 'stop' invocada: Parando máquinas virtuales...")
    
    for mv in mvs:
        mv.stop_vm()

    log.debug(f"Cliente parado correctamente")
    subprocess.run(
        ["sudo", "ovs-vsctl", "del-br", "LAN1"],
    )
    log.debug("Bridge LAN1 eliminado")
    subprocess.run(
        ["sudo", "ovs-vsctl", "del-br", "LAN2"],
    )
    log.debug("Bridge LAN2 eliminado")

def destroy(config, log):
    print("Función 'destroy' invocada: Liberando escenario...")
    
    for mv in mvs:
        mv.destroy_vm()

def main():
    # Validar que se pasa un argumento
    if len(sys.argv) != 2:
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


    #Configurar logging
    debug_mode = config.get("debug", False)
    log = init_log(debug_mode)

    # Verificar si el comando es válido e invocar la función correspondiente
    # HAY QUE PASAR CONFIG A QUIEN LO NECESITE

    if command in commands:
        commands[command](config, log)  # Invocar la función asociada
    else:
        print(f"Comando desconocido: {command}")
        print("Opciones válidas: create, start, stop, destroy")
        sys.exit(1)

if __name__ == "__main__":
    main()
