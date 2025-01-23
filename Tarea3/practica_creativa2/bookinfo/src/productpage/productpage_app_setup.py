import subprocess
import logging
import os
import contextlib

#Crear variable de entorno
os.environ["GRUP_NUM"] = "39"

#Configuración del logger
log = logging.getLogger('manage-p2')

# Ruta base del script
REPO_URL = "https://github.com/CDPS-ETSIT/practica_creativa2"
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PRODUCTPAGE_DIR = os.path.join(BASE_DIR, "")

# Cambia el directorio temporalmente	
@contextlib.contextmanager
def change_directory(target_dir):
    """Cambia de directorio temporalmente y regresa al original"""
    original_dir = os.getcwd()
    os.chdir(target_dir)
    try:
        yield
    finally:
        os.chdir(original_dir)


def actualizar_sistema():
	#sudo apt-get update	
	subprocess.run(["sudo", "apt-get", "update"], check=True)
	subprocess.run(["sudo", "apt","install", "python3-pip"], check=True)

def clonar_repositorio(repo_url="https://github.com/CDPS-ETSIT/practica_creativa2", base_dir=BASE_DIR):
    with change_directory(base_dir):
        if not os.path.exists("practica_creativa2"):
            subprocess.run(["git", "clone", repo_url], check=True)
            print(f"Repositorio clonado en {base_dir}/practica_creativa2")
        else:
            print(f"Repositorio ya existe en {base_dir}/practica_creativa2")
	

def instala_dependencias(productpage_dir=PRODUCTPAGE_DIR):
	#Parseo requirements.txt
	# pip3 install -r requirements.txt
	requirements = "requirements.txt"

	with change_directory(productpage_dir):
		# Eliminar la versión de 'requests' en requirements.txt
		subprocess.run(["sed", "-i", "s/requests==[0-9.]*$/requests/", "requirements.txt"], check=True)
		#Cambiar la versión de 'json2html' en requirements.txt
		subprocess.run(["sed", "-i", "s/json2html==1.2.1/json2html==1.3.0/", "requirements.txt"], check=True)

		try:
			subprocess.run(["pip3", "install", "-r", requirements], check=True)
			log.debug(f"Dependencias instaladas correctamente desde {requirements}.")
		except Exception as e:
			log.error(f"Error al instalar dependencias desde {requirements}: {e}")
			exit(1)


def edicion_archivos(productpage_dir=PRODUCTPAGE_DIR):

	with change_directory(productpage_dir):
		#Editar archivos

		#sed -i 's/{% block title %}Simple Bookstore App{% endblock %}/{% block title %}Grupo {{ grup_num }}{% endblock %}/' templates/index.html
		subprocess.run(["sed", "-i", "s/{% block title %}Simple Bookstore App{% endblock %}/{% block title %}Grupo {{ grup_num }}{% endblock %}/", "templates/index.html"], check=True)	
		#sed -i 's/{% block title %}Simple Bookstore App{% endblock %}/{% block title %}Grupo {{ grup_num }}{% endblock %}/' templates/productpage.html
		subprocess.run(["sed", "-i", "s/{% block title %}Simple Bookstore App{% endblock %}/{% block title %}Grupo {{ grup_num }}{% endblock %}/", "templates/productpage.html"], check=True)	

		#Editar productpage_monolith.py
		#sed -i '/app = Flask(__name__)/a \\\ngrup_num = os.getenv("GRUP_NUM", "Default Group")\napp.config[\'TEMPLATES_AUTO_RELOAD\'] = True\n' productpage_monolith.py
		subprocess.run(
			"sed -i '/app = Flask(__name__)/a \\grup_num = os.getenv(\"GRUP_NUM\", \"Default Group\")\\napp.config[\"TEMPLATES_AUTO_RELOAD\"] = True\\n' productpage.py",
			shell=True,
			check=True
		)
		
		# Modificar la línea de index.html.
		subprocess.run(
		"sed -i \"s|return render_template('index.html', serviceTable=table)|return render_template('index.html', serviceTable=table, grup_num=grup_num)|\" productpage.py",
			shell=True,
			check=True
		)

		# Modificar la línea de productpage.html. 
		subprocess.run(
			"sed -i \"s|user=user)|user=user, grup_num=grup_num)|\" productpage.py",
			shell=True,
			check=True
		)

def arranca_app():
	with change_directory(PRODUCTPAGE_DIR):
		#Arrancar la app
		subprocess.run(["python3", "productpage_monolith.py", "9080"], check=True)
		log.debug("App arrancada correctamente.")
		os.chdir("/home/cdps/")
		log.debug("Cambiado al directorio raíz.")
		log.info("App arrancada correctamente.")


if __name__ == "__main__":
	try:
		actualizar_sistema()
		clonar_repositorio(repo_url=REPO_URL, base_dir=BASE_DIR)
		instala_dependencias(productpage_dir=PRODUCTPAGE_DIR)
		edicion_archivos(productpage_dir=PRODUCTPAGE_DIR)
		arranca_app()

	except Exception as e:
		log.error(f"Error al arrancar la app: {e}")
		exit(1)

