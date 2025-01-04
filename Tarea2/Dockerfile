FROM python:3.7.7-slim
WORKDIR /
#Instala dependencias
RUN apt-get update
COPY . .
RUN pip3 install -r practica_creativa2/bookinfo/src/productpage/requirements.txt
EXPOSE 9080
CMD python3 practica_creativa2/bookinfo/src/productpage/productpage_monolith.py 9080