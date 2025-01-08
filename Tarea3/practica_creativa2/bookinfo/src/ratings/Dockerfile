FROM node:12.18.1-slim
WORKDIR /opt/microservices
COPY . .
ENV SERVICE_VERSION=v1
RUN npm install
EXPOSE 9080
CMD node run /opt/microservices/ratings.js 9080