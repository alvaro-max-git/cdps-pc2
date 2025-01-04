import os
import shutil
import subprocess

def setup_environment():
    # Definir rutas
    base_dir = "/mnt/tmp/alvaro.pablo"
    
    src_files = [
        "/lab/cdps/pc1/plantilla-vm-pc1.xml",
        os.path.join(os.getcwd(), "PC2.xml") # Ruta relativa al archivo XML
    ]
    
    # Crear la carpeta de destino si no existe
    if not os.path.exists(base_dir):
        print(f"Creando directorio: {base_dir}")
        os.makedirs(base_dir) # Crear directorio
    else:
        print(f"El directorio ya existe: {base_dir}")
    
    # Copiar archivos
    for file in src_files:
        dest_file = os.path.join(base_dir, os.path.basename(file))
        print(f"Copiando {file} a {dest_file}")
        shutil.copy(file, dest_file)
    
    # Ejecutar comando para preparar el entorno
    print("Ejecutando /lab/cnvr/bin/prepare-vnx-debian...")
    try:
        subprocess.run(["/lab/cnvr/bin/prepare-vnx-debian"], check=True)
        print("Entorno preparado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al preparar el entorno: {e}")

# Ejecutar la función si se ejecuta el script directamente
# (no se ejecuta si se importa como módulo)

if __name__ == "__main__":
    setup_environment()