from lxml import etree
import shutil
import subprocess
import os
import logging

log = logging.getLogger('manage-p2')

def create_xml(base_xml, vm_name, image, bridges):
	new_xml = f"{vm_name}.xml"

	try:
		print(f"Creando definición XML de {vm_name}...")
		
		# Copiar el xml base
		shutil.copy(base_xml, new_xml)

		# Parsear el xml copiado
		tree = etree.parse(new_xml)
		root = tree.getroot()

		# Modificar el nombre de la máquina virtual
		name = root.find("name")
		name.text = vm_name

		# Modificar el nombre del disco
		disk = root.find("./devices/disk/source")
		disk.set("file", image)

		# Modificar las interfaces de red
		devices = root.find("devices")
		interface_or = devices.find("interface")
		devices.remove(interface_or)

		for bridge in bridges:
			new_interface = etree.Element("interface", type="bridge")

			source = etree.SubElement(new_interface, "source")
			source.set("bridge", bridge)

			model = etree.SubElement(new_interface, "model")
			model.set("type", "virtio")

			virtualport = etree.SubElement(new_interface, "virtualport")
			virtualport.set("type", "openvswitch")

			devices.append(new_interface)

			tree.write(new_xml, pretty_print=True, xml_declaration=True, encoding="utf-8")
			print(f"XML de definición {new_xml} creado")
			return new_xml

	except Exception as e:
		print("Error al crear el archivo XML para {vm_name}")
		print(e)

def main ():
	base_xml = "plantilla-vm-pc1.xml"
	num_vms = 2
	for i in range(num_vms):
		create_xml(base_xml, f"s{i+1}", f"s{i+1}.qcow2", ["LAN1"])
		create_xml(base_xml, "lb", "lb.qcow2", ["LAN1", "LAN2"])
		create_xml(base_xml, "c1", "c1.qcow2", ["LAN2"])
	
def copia_app(app, dst, vm_name):
	#Ruta de la app	
	app_path = os.path.join(os.getcwd(), "productpage")
     # Copiar la carpeta de la app a la máquina virtual
	try:
		subprocess.run(["sudo", "virt-copy-in", "-a", f"{vm_name}.qcow2", 
			app, "/"], check=True)
	except subprocess.CalledProcessError as e:
		log.error(f"Error al copiar la carpeta de la app a {vm_name}: {e}")
	log.debug(f"Carpeta de la app copiada a {vm_name}.")



if __name__ == "__main__":
	main()