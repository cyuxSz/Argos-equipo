# Imagen de la API: Node 24 LTS (multi-arquitectura: sirve en tu PC y en el servidor)
FROM node:24.22.2-alpine
WORKDIR /app
# Primero solo las dependencias: Docker reutiliza esta capa si el codigo cambia y las dependencias no
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY RestApi.js alertas.js ./
USER node
EXPOSE 3000
CMD ["node", "RestApi.js"]
