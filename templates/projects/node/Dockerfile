FROM node:24-alpine

WORKDIR /app

RUN apk upgrade --no-cache

COPY package*.json ./

RUN npm ci

COPY . .

USER node

EXPOSE 3000

CMD ["npm", "start"]