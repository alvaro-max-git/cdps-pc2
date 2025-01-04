import subprocess
import logging
import os

#Configuración del logger
log = logging.getLogger('manage-p2')

def instala_dependencias(requirements):
	#Parseo requirements.txt
	# pip3 install -r requirements.txt
	try:
		subprocess.run(["pip3", "install", "-r", requirements], check=True)
		log.debug(f"Dependencias instaladas correctamente desde {requirements}.")
	except Exception as e:
		log.error(f"Error al instalar dependencias desde {requirements}: {e}")
		exit(1)
	
		
def arranca_app():
	#Arrancar la app
	#sudo apt-get update	
	subprocess.run(["sudo", "apt-get", "update"], check=True)
	subprocess.run(["sudo", "apt","install", "python3-pip"], check=True)
	if not os.path.exists("practica_creativa2"):
		subprocess.run(["git", "clone", "https://github.com/CDPS-ETSIT/practica_creativa2"], check=True)
	log.debug("Cambiado al directorio de la app.")
	# Cambiamos el working directory a productpage
	os.chdir("practica_creativa2/bookinfo/src/productpage")
	# Eliminar la versión de 'requests' en requirements.txt
	subprocess.run(["sed", "-i", "s/requests==[0-9.]*$/requests/", "requirements.txt"], check=True)
	#Cambiar la versión de 'json2html' en requirements.txt
	subprocess.run(["sed", "-i", "s/json2html==1.2.1/json2html==1.3.0/", "requirements.txt"], check=True)
	instala_dependencias("requirements.txt")
	#Editar archivos

	#sed -i 's/{% block title %}Simple Bookstore App{% endblock %}/{% block title %}Grupo {{ grup_num }}{% endblock %}/' templates/index.html
	subprocess.run(["sed", "-i", "s/{% block title %}Simple Bookstore App{% endblock %}/{% block title %}Grupo {{ grup_num }}{% endblock %}/", "templates/index.html"], check=True)	
	#sed -i 's/{% block title %}Simple Bookstore App{% endblock %}/{% block title %}Grupo {{ grup_num }}{% endblock %}/' templates/productpage.html
	subprocess.run(["sed", "-i", "s/{% block title %}Simple Bookstore App{% endblock %}/{% block title %}Grupo {{ grup_num }}{% endblock %}/", "templates/productpage.html"], check=True)	

	#Editar productpage_monolith.py
	#sed -i '/app = Flask(__name__)/a \\\ngrup_num = os.getenv("GRUP_NUM", "Default Group")\napp.config[\'TEMPLATES_AUTO_RELOAD\'] = True\n' productpage_monolith.py
	subprocess.run(
		"sed -i '/app = Flask(__name__)/a \\grup_num = os.getenv(\"GRUP_NUM\", \"Default Group\")\\napp.config[\"TEMPLATES_AUTO_RELOAD\"] = True\\n' productpage_monolith.py",
		shell=True,
		check=True
	)
	
	# Modificar la línea de index.html. ESTA LÍNEA NO FUNCIONA
	subprocess.run(
		"sed -i \"/return render_template(\\'index.html\\', serviceTable=table)/s/)/, grup_num=grup_num)/\" productpage_monolith.py",
		shell=True,
		check=True
	)

	# Modificar la línea de productpage.html. ESTA LÍNEA NO FUNCIONA
	subprocess.run(
		"sed -i \"/return render_template(\\'productpage.html\\'/, /user=user/s/)/, grup_num=grup_num)/\" productpage_monolith.py",
		shell=True,
		check=True
	)

	#crear variable de entorno
	subprocess.run("export GRUP_NUM=39", shell=True, check=True)

	#Arrancar la app
	subprocess.run(["python3", "productpage_monolith.py", "9080"], check=True)
	log.debug("App arrancada correctamente.")
	os.chdir("/home/cdps/")
	log.debug("Cambiado al directorio raíz.")
	log.info("App arrancada correctamente.")

if __name__ == "__main__":
	try:
		arranca_app()
	except Exception as e:
		log.error(f"Error al arrancar la app: {e}")
		exit(1)

