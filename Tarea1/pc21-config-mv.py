import os
import subprocess
import shutil

# Directorios y archivos
base_dir = os.getcwd()  # Directorio actual
setup_script = os.path.join(base_dir, "productpage_app_setup.py")  # Ruta al setup script
vm_image = "/mnt/tmp/alvaro.pablo/PC2.qcow2"  # Ruta a la imagen de la VM
xml_file = "/mnt/tmp/alvaro.pablo/PC2.xml"  # Ruta al archivo XML de definición

# Comprobaciones previas
def check_files():
    if not os.path.exists(setup_script):
        raise FileNotFoundError(f"El archivo {setup_script} no existe.")
    if not os.path.exists(vm_image):
        raise FileNotFoundError(f"La imagen de la VM {vm_image} no existe.")
    if not os.path.exists(xml_file):
        raise FileNotFoundError(f"El archivo XML {xml_file} no existe.")

def copy_setup_script():
    print("Copiando el script en la imagen de la VM...")
    command = [
        "sudo", "virt-copy-in", "-a", vm_image, setup_script, "/home/cdps"
    ]
    subprocess.run(command, check=True)
    print("Archivo copiado correctamente.")

def manage_vm():
    print("Reconfigurando y arrancando la máquina virtual...")

    # Undefine por si acaso ya existe
    subprocess.run(["sudo", "virsh", "undefine", "PC2"], check=False)

    # Define la máquina virtual
    subprocess.run(["sudo", "virsh", "define", xml_file], check=True)

    # Arranca la máquina virtual
    subprocess.run(["sudo", "virsh", "start", "PC2"], check=True)

    print("Máquina virtual configurada y arrancada correctamente.")

    try:
        subprocess.Popen(
            ["xterm", "-T", "Console PC2", "-geometry", "200x50", "-e", "sudo", "virsh", "console", "PC2"]
        )
        print("Consola abierta en una ventana separada.")
    except FileNotFoundError:
        print("Error: xterm no está instalado. No se puede abrir la consola.")

# Ejecución principal
if __name__ == "__main__":
    try:
        print("Comprobando archivos necesarios...")
        check_files()
        
        print("Preparando la configuración de la máquina virtual...")
        copy_setup_script()
        
        print("Gestionando la máquina virtual...")
        manage_vm()

        print("Proceso completado con éxito.")
    except Exception as e:
        print(f"Se produjo un error: {e}")
