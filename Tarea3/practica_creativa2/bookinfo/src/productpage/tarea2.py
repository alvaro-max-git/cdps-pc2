import os

from productpage_app_setup import clonar_repositorio, edicion_archivos

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PRODUCTPAGE_DIR = os.path.join(BASE_DIR, "practica_creativa2/bookinfo/src/productpage")
REPO_URL = "https://github.com/CDPS-ETSIT/practica_creativa2"

if __name__ == "__main__":
    try:
        edicion_archivos(productpage_dir=PRODUCTPAGE_DIR)

    except Exception as e:
        print(f"Error al arrancar la app: {e}")
        exit(1)