FROM node:18

WORKDIR /app
COPY ./app/package* ./
RUN npm install

COPY ./app ./

# NOTE: this should point the static files
ARG VITE_STATIC_HOST=https://nginx:4000
ENV VITE_STATIC_HOST=${VITE_STATIC_HOST}
ARG VITE_CACHE_BUCKET=manga-recs-cache
ENV VITE_CACHE_BUCKET=${VITE_CACHE_BUCKET}
ENV PORT=${PORT:-8000}
RUN npm run build
CMD node build/index.js
