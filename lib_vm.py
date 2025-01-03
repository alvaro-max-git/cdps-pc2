import logging
import subprocess
import sys
import os


log = logging.getLogger('manage-p2')

class VM: 
  def __init__(self, name):
    self.name = name
    log.debug('init VM ' + self.name)


  def create_vm (self, image, interfaces):
    # nota: interfaces es un array de diccionarios de python
    #       añadir los campos que se necesiten
    log.debug("create_vm " + self.name + " (image: " + image + ")")
    new_image = f"{self.name}.qcow2"
    try:
        print(f"Creando imagen para {self.name}...")
        subprocess.run(
            ["qemu-img", "create", "-F", "qcow2", "-f", "qcow2", "-b", image, new_image],
            check=True
        )
        print(f"Imagen creada: {new_image}")
    except subprocess.CalledProcessError as e:
        print(f"Error al crear la imagen para {self.name}: {e}")
        sys.exit(1)
    subprocess.run(
                ["sudo", "virsh", "define", f"{self.name}.xml"],
                check=True
            )
    #Directorio temporal
    tmp_dir = "tmp"
    os.makedirs(tmp_dir, exist_ok=True)
    #Configuración de red
    for lan in interfaces:
      for i in lan:
        log.debug("  if: addr=" + i["addr"] + ", mask=" + i["mask"]) 
        if self.name == "lb":
          return
        else:
          primary_interface = interfaces[0]
          ip = primary_interface["addr"]
          mask = primary_interface["mask"]
          gateway = "10.1.2.1"  # Definir un gateway genérico

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
          log.info(f"Archivo 'interfaces' copiado a {self.name}.")

          subprocess.run(["sudo", "virt-copy-in", "-a", f"{self.name}.qcow2", 
              os.path.join(tmp_dir, "hostname"), "/etc"], check=True)
          log.info(f"Archivo 'hostname' copiado a {self.name}.")

          # Modificar /etc/hosts
          subprocess.run(["sudo", "virt-edit", "-a", f"{self.name}.qcow2", 
            "/etc/hosts", f"-e", f"s/127.0.1.1.*/127.0.1.1 {self.name}/"], check=True)
          log.info(f"Archivo 'hosts' modificado para {self.name}.")



  def start_vm (self):
    log.debug("start_vm " + self.name)
    subprocess.run(
                ["sudo", "virsh", "start", self.name],
                check=True
            )
    self.show_console_vm()
    

  def show_console_vm (self):
    log.debug("show_console_vm " + self.name)
    subprocess.run(
                ["sudo", "virsh", "console", self.name, "&"],
                check=True
            )

  def stop_vm (self):
    log.debug("stop_vm " + self.name)
    subprocess.run(
                ["sudo", "virsh", "undefine", self.name],
                check=True
            )

  def destroy_vm (self):
    log.debug("destroy_vm " + self.name)
    subprocess.run(
                ["sudo", "virsh", "destroy", self.name],
                check=True
            )

class NET:
  def __init__(self, name):
    self.name = name
    log.debug('init net ' + self.name)

  def create_net(self):
      log.debug('create_net ' + self.name)

  def destroy_net(self):
      log.debug('destroy_net ' + self.name)
