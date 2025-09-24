# build env
FROM node:20.17.0-alpine
WORKDIR /app
RUN npm install -g npm@11.6.0 \
    && npm config set fetch-retry-maxtimeout 60000 \
    && npm config set fetch-retry-mintimeout 20000
COPY package*.json ./
RUN npm ci --no-audit --no-fund
COPY . ./
RUN npm run build
CMD cp -r build result_build
