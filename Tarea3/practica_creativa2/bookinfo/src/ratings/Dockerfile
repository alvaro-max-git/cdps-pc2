FROM node:12.18.1-slim
WORKDIR /opt/microservices
COPY . .
ENV SERVICE_VERSION=v1
EXPOSE 9080
RUN npm install
CMD [ "npm", "start" ]