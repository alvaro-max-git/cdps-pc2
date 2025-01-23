#Imagen a usar
FROM python:3.7.7-slim
#Directorio de trabajo
WORKDIR /
#Variable de entorno GROUP_NUM
ENV GRUP_NUM=39
#Instala dependencias
RUN apt-get update && apt-get install -y python3 python3-pip git && apt-get clean
#Copiamos todos los archivos de este directorio al directorio de trabajo
COPY . .
#Ejecutar el script de configuración > edita los archivos
RUN python3 tarea2.py
#Instalamos las dependencias necesarias
RUN pip3 install -r requirements.txt
#Exponemos el puerto 9080
EXPOSE 9080
#Ejecutamos el archivo productpage.py para arrancar la app en el servidor.
CMD python3 productpage.py 9080