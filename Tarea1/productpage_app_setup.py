#A medio hacer: script que se debe copiar a cada s para getionar la app
import subprocess
import logging

#Configuración del logger
log = logging.getLogger('manage-p2')

def instala_dependencias(requirements):
	#Parseo requirements.txt
	modulos = []
	try:
		with open(requirements) as f:
			modulos.append(f.readlines())
		log.debug("Requirements leídos correctamente.")
	except Exception as e:
		log.error(f"Error al leer el archivo requirements.txt: {e}")
		return
	#Instalo dependencias	
	try:
		log.info("Instalando dependencias...")
		for modulo in modulos:
			subprocess.run(["pip3", "install", modulo], check=True)
		log.info("Dependencias instaladas correctamente.")
	except subprocess.CalledProcessError as e:
		log.error(f"Error al instalar las dependencias: {e}")
		
def arranca_app():
	#Arrancar la app
	subprocess.run(["cd", "/productpage"], check=True)
	log.debug("Cambiado al directorio de la app.")
	subprocess.run(["python3", "productpage_monolith.py", "9080"], check=True)
	log.debug("App arrancada correctamente.")
	subprocess.run(["cd", "/"], check=True)
	log.debug("Cambiado al directorio raíz.")
	log.info("App arrancada correctamente.")

def main():
	instala_dependencias("requirements.txt")
	arranca_app()
