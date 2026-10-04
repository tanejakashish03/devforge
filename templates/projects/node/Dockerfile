FROM node:24-alpine

WORKDIR /app

RUN apk upgrade --no-cache

COPY package*.json ./

RUN npm ci --omit=dev \
    && npm cache clean --force \
    && rm -rf /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/corepack \
       /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack \
       /usr/local/bin/yarn /usr/local/bin/yarnpkg /opt/yarn-*

COPY . .

USER node

EXPOSE 3000

CMD ["node", "src/index.js"]