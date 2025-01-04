FROM pyton:3.7.7-slim

#Instala dependencias
RUN apt-get update
RUN git clone https://github.com/CDPS-ETSIT/practica_creativa2.git
RUN pip3 install -r practica_creativa2/bookinfo/src/productpage/requirements.txt
EXPOSE 9080
CMD python3 practica_creativa2/bookinfo/src/productpage/productpage_monolith.py