#A medio hacer: script que se debe copiar a cada s para getionar la app

def instala_dependencias(requirements):
	#Parseo requirements.txt
	modulos = []
	try:
		with open(requirements) as f:
			modulos.append(f.readlines())
	except Exception as e:
		print(f"Error al leer el archivo {requirements}")
		print(e)
		return
	#Instalo dependencias	
	try:
		print("Instalando dependencias...")
		for modulo in modulos:
			subprocess.run(["pip3", "install", modulo], check=True)
		print("Dependencias instaladas correctamente.")
	except subprocess.CalledProcessError as e:
		print(f"Error al instalar las dependencias: {e}")
		
def arranca_app():
	#Arrancar la app
	subprocess.run(["cd", "/productpage"], check=True)
	log.debug("Cambiado al directorio de la app.")
	subprocess.run(["python3", "productpage_monolith.py", "9080"], check=True)
	log.debug("App arrancada correctamente.")
	subprocess.run(["cd", "/"], check=True)
	log.debug("Cambiado al directorio raíz.")
	log.info("App arrancada correctamente.")