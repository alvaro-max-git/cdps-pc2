#Imagen a usar
FROM ruby:2.7.1-slim
#Directorio de trabajo
WORKDIR /opt/microservices
#Variables de entorno
ENV SERVICE_VERSION = v1
ENV ENABLE_EXTERNAL_BOOK_SERVICE = true 
#Copiamos todos los archivos de este directorio a donde dice en el enunciado
COPY . .
#Exponemos el puerto 9080
EXPOSE 9080
#Ejecutamos el archivo productpage_monolith.py para arrancar la app en el servidor.
CMD ruby /opt/microservices/details.rb 9080