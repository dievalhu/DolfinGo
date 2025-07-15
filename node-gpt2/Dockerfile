FROM node:12-alpine3.14

#directorio de trabajo
WORKDIR /app-node

#Copiar al directorio de trabajo
COPY package*.json ./

#Se crea el node_moudles dentro del container
#RUN npm config rm proxy 
#RUN npm config rm https-proxy --tried removing npm proxy
RUN npm install 

#Copiar al directorio actual
COPY . .

#CMD [ "npm", "start" ]
