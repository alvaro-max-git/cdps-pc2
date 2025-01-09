#Imagen a usar
FROM python:3.7.7-slim
#Directorio de trabajo
WORKDIR /
#Variable de entorno GROUP_NUM, aún no hace nada.
ENV GRUP_NUM=39 
#Instala dependencias
RUN apt-get update && apt-get install -y python3 python3-pip git && apt-get clean
#Copiamos todos los archivos de este directorio al directorio de trabajo
COPY . .
#Ejecutar el script de configuración > clona el repositorio y edita los archivos
RUN python3 tarea2.py
#Instalamos las dependencias necesarias
RUN pip3 install -r practica_creativa2/bookinfo/src/productpage/requirements.txt
#Exponemos el puerto 9080
EXPOSE 9080
#Ejecutamos el archivo productpage_monolith.py para arrancar la app en el servidor.
CMD python3 practica_creativa2/bookinfo/src/productpage/productpage_monolith.py 9080