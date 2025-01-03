import logging
import os
import subprocess
import sys
from utilidades import create_xml

log = logging.getLogger('manage-p2')

class VM: 
  def __init__(self, name):
    self.name = name
    log.debug('init VM ' + self.name)
 
  def create_vm (self, image, interfaces):
    # nota: interfaces es un array de diccionarios de python
    #       añadir los campos que se necesiten
    log.debug("create_vm " + self.name + " (image: " + image + ")")
    for i in interfaces:
      log.debug("  if: addr=" + i["addr"] + ", mask=" + i["mask"]) 
    

   #Creamos el archivo imagen 
    base_image = "cdps-vm-base-pc1.qcow2"
    new_image = f"{self.name}.qcow2"
    try:
        log.debug(f"Creando imagen para {self.name}...")
        subprocess.run(
            ["qemu-img", "create", "-F", "qcow2", "-f", "qcow2", "-b", base_image, new_image]
        )
        log.debug(f"Imagen creada: {new_image}")
    except subprocess.CalledProcessError as e:
        log.info(f"Error al crear la imagen para {self.name}: {e}")
        sys.exit(1)

  #Creamos definicion xml
    log.debug(f"Creando definición XML para {self.name}...")
    base_xml = "plantilla-vm-pc1.xml"
    if self.name == "lb":
      bridges =["LAN1", "LAN2"]
    elif self.name == "c1":
      bridges =["LAN1"]
    else:
      bridges =["LAN2"] 
    create_xml(base_xml, self.name, f"/mnt/tmp/alvaro.pablo/{image}", bridges)
    log.debug(f"Definición XML creada para {self.name}.")

  #Hace undefine de la MV si ya existe
    try:
      subprocess.run(
      ["sudo", "virsh", "undefine", self.name],
      check=True,
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL
      )
      log.debug(f"MV {self.name} indefinida correctamente.")
    except subprocess.CalledProcessError:
      log.debug(f"MV {self.name} no definida previamente.")
    except Exception as e:
      log.debug(f"Error al intentar undefinir MV {self.name}: {e}")

   #Definimos MV
    log.debug(f"Definiendo MV {self.name}.xml")
    subprocess.run(
      ["sudo", "virsh", "define", f"{self.name}.xml"],
        check=True
      )
    log.debug(f"MV {self.name}.xml definida correctamente") 

    #creamos directorio temporal
    log.debug(f"Creando directorio temporal para {self.name}.")
    tmp_dir = "tmp"
    os.makedirs(tmp_dir, exist_ok=True)

    log.debug(f"Configurando red para {self.name}...")
    #UN POCO CUTRE EL IF:
    if len(interfaces) == 1:
      # Usar la primera interfaz para configurar la red
      primary_interface = interfaces[0]
      ip = primary_interface["addr"]
      mask = primary_interface["mask"]
      
      if self.name == "c1":
        gateway = "10.1.1.1"
      else:
        gateway = "10.1.2.1"
      # Crear archivo /etc/network/interfaces
      interfaces_content = f"""
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
  address {ip}
  netmask {mask}
  gateway {gateway}
"""
      with open(os.path.join(tmp_dir, "interfaces"), "w") as f:
        f.write(interfaces_content.strip())
      log.debug(f"Archivo 'interfaces' creado para {self.name} con IP {ip}.")

      # Crear archivo /etc/hostname
      with open(os.path.join(tmp_dir, "hostname"), "w") as f:
        f.write(self.name)
      log.debug(f"Archivo 'hostname' creado para {self.name}.")

      # Copiar los archivos a la imagen
      subprocess.run(["sudo", "virt-copy-in", "-a", f"{self.name}.qcow2", 
          os.path.join(tmp_dir, "interfaces"), "/etc/network"], check=True)
      log.debug(f"Archivo 'interfaces' copiado a {self.name}.")

      subprocess.run(["sudo", "virt-copy-in", "-a", f"{self.name}.qcow2", 
          os.path.join(tmp_dir, "hostname"), "/etc"], check=True)
      log.debug(f"Archivo 'hostname' copiado a {self.name}.")

      # Modificar /etc/hosts
      subprocess.run(["sudo", "virt-edit", "-a", f"{self.name}.qcow2", 
        "/etc/hosts", f"-e", f"s/127.0.1.1.*/127.0.1.1 {self.name}/"], check=True)
      log.debug(f"Archivo 'hosts' modificado para {self.name}.")

      #Modificando /etc/rc.local para arrancar un servidor apache2
      subprocess.run(["sudo", "virt-edit", "-a", f"{self.name}.qcow2", 
          "/etc/rc.local", "-e", "s/^exit 0$/sudo systemctl start apache2\\nexit 0/"], check=True)
      log.debug(f"Archivo 'rc.local' modificado para {self.name}.")

      # Crear el fichero index.html en un directorio temporal
      index_html_content = f"""
      <!DOCTYPE html>
      <html>
      <head>
          <title>Bienvenido a {self.name}</title>
      </head>
      <body>
          <h1>Hola mundo!</h1>
          <p>Soy {self.name}</p>
      </body>
      </html>
      """

      index_html_path = os.path.join(tmp_dir, "index.html")
      with open(index_html_path, "w") as f:
          f.write(index_html_content)
      log.debug(f"Archivo 'index.html' creado en {index_html_path}.")

      # Copiar el fichero index.html a /var/www/html/index.html en la máquina virtual
      subprocess.run(["sudo", "virt-copy-in", "-a", f"{self.name}.qcow2", 
          index_html_path, "/var/www/html"], check=True)
      log.debug(f"Archivo 'index.html' copiado a {self.name}.")
      log.info(f"Página de bienvenida de {self.name} estará disponible en {ip}:80 al arrancar la maquina virtual.")
  
    else:
      #cutre else, configuro el lb
      interfaces_content = f"""
auto lo
iface lo inet loopback
"""
      for interface in interfaces:
        ip = interface["addr"]
        mask = interface["mask"]
        eth = f"eth{interfaces.index(interface)}"

        interfaces_content += f"""
auto {eth}
iface {eth} inet static
  address {ip}
  netmask {mask}
"""

      with open(os.path.join(tmp_dir, "interfaces"), "w") as f:
        f.write(interfaces_content.strip())
      log.debug(f"Archivo 'interfaces' creado para {self.name}")

      # Crear archivo /etc/hostname
      with open(os.path.join(tmp_dir, "hostname"), "w") as f:
        f.write(self.name)
      log.debug(f"Archivo 'hostname' creado para {self.name}.")

      # Copiar los archivos a la imagen
      subprocess.run(["sudo", "virt-copy-in", "-a", f"{self.name}.qcow2", 
          os.path.join(tmp_dir, "interfaces"), "/etc/network"], check=True)
      log.debug(f"Archivo 'interfaces' copiado a {self.name}.")

      subprocess.run(["sudo", "virt-copy-in", "-a", f"{self.name}.qcow2", 
          os.path.join(tmp_dir, "hostname"), "/etc"], check=True)
      log.debug(f"Archivo 'hostname' copiado a {self.name}.")

      # Modificar /etc/hosts
      subprocess.run(["sudo", "virt-edit", "-a", f"{self.name}.qcow2", 
        "/etc/hosts", f"-e", f"s/127.0.1.1.*/127.0.1.1 {self.name}/"], check=True)
      log.debug(f"Archivo 'hosts' modificado para {self.name}.")

      log.debug("Habilitando IP forwarding en /etc/sysctl.conf.")
      subprocess.run(["sudo", "virt-edit", "-a", f"{self.name}.qcow2", 
          "/etc/sysctl.conf", "-e", 
          "s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/"], check=True)
      log.debug(f"IP forwarding habilitado en {self.name}.")
      log.info(f"MV {self.name} creada correctamente.")

  def start_vm (self):
    log.debug("start_vm " + self.name)
    #Arranca la máquina virtual utilizando 'virsh start'.
    try:
        log.debug(f"Intentando arrancar la máquina virtual {self.name}...")
        subprocess.run(["sudo", "virsh", "start", self.name], check=True)
        log.debug(f"Máquina virtual {self.name} arrancada correctamente.")
    except subprocess.CalledProcessError as e:
        log.debug(f"Error al arrancar la máquina virtual {self.name}: {e}")
    except Exception as e:
        log.debug(f"Excepción inesperada al arrancar {self.name}: {e}")
    log.info(f"MV {self.name} arrancada correctamente.")
    
    self.show_console_vm()

  def show_console_vm (self):
    log.debug("show_console_vm " + self.name)
    subprocess.Popen(
                ["xterm", "-T", f"Console {self.name}", "-geometry", "200x50", "-e", "sudo", "virsh", "console", self.name]
            )
    log.debug(f"Consola de MV {self.name} abierta.")

  def stop_vm (self):
    log.debug("Parando " + self.name)
    try:
      # Cierra las ventanas de las consolas
      subprocess.run(
                  ["pkill", "-f", f"xterm.*Console {self.name}"],
                  check=True
              )
      # Apaga las MVs (pero conserva imágenes y config)
      subprocess.run(
                  ["sudo", "virsh", "shutdown", self.name],
                  check=True,
                  stdout=subprocess.DEVNULL,
                  stderr=subprocess.DEVNULL
              )
    except subprocess.CalledProcessError as e:
      log.warning(f"MV {self.name} problemas al parar: {e}")
    log.info(f"MV {self.name} parada correctamente.")

  def destroy_vm (self):
    log.debug("destroy_vm " + self.name)

      
    try:
      subprocess.run(
        ["sudo","virsh","undefine", self.name],
        check=True
        )
    except subprocess.CalledProcessError as e:
      log.warning(f"Error destruyendo MV {self.name}:{e}")

    try:
      subprocess.run(
        ["sudo","virsh","destroy", self.name],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
      log.debug(f"Error destruyendo MV {self.name}:{e}")


    #Eliminar archivos
    try:
      subprocess.run([ "rm", f"{self.name}.qcow2"], check=True)
      log.debug(f"Archivo {self.name}.qcow2 eliminado.")
    except subprocess.CalledProcessError:
      log.warning(f"Archivo {self.name}.qcow2 no encontrado o no se pudo eliminar.")
    try:
      subprocess.run(["rm", f"{self.name}.xml"], check=True)
      log.debug(f"Archivo {self.name}.xml eliminado.")
    except subprocess.CalledProcessError:
      log.warning(f"Archivo {self.name}.xml no encontrado o no se pudo eliminar.")
    log.info(f"MV {self.name} destruida correctamente.")
      

class NET:
  def __init__(self, name):
    self.name = name
    log.info('Iniciando red' + self.name)

  #crea la red del host  
  def create_net(self):
      
      log.debug("Borrando bridges virtuales por si ya existieran")
      subprocess.run(
          ["sudo", "ovs-vsctl", "del-br", "LAN1"],
          stdout=subprocess.DEVNULL,
          stderr=subprocess.DEVNULL
      )
      log.debug("Bridge LAN1 eliminado")
      subprocess.run(
          ["sudo", "ovs-vsctl", "del-br", "LAN2"],
          stdout=subprocess.DEVNULL,
          stderr=subprocess.DEVNULL
      )

      log.debug("Creando bridges virtuales")
      subprocess.run(
            ["sudo", "ovs-vsctl", "add-br", "LAN1"],
            check=True
        )
      subprocess.run(
            ["sudo", "ovs-vsctl", "add-br", "LAN2"],
            check=True
      )
      subprocess.run(
            ["sudo", "ifconfig", "LAN1", "up"],
            check=True
      )
      subprocess.run(
            ["sudo", "ifconfig", "LAN1", "10.1.1.3/24"],            
            check=True
      )
      subprocess.run(
            ["sudo", "ip", "route", "add", "10.1.0.0/16", "via", "10.1.1.1"],
            check=True
      )
      log.info("Red creada correctamente")


  def destroy_net(self):
      log.debug('destroy_net ' + self.name)
      subprocess.run(
          ["sudo", "ovs-vsctl", "del-br", "LAN1"],
      )
      log.debug("Bridge LAN1 eliminado")
      subprocess.run(
          ["sudo", "ovs-vsctl", "del-br", "LAN2"],
      )
      log.debug("Bridge LAN2 eliminado")
      log.info("Red destruida correctamente")

