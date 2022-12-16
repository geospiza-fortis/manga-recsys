FROM node:18

WORKDIR /app
COPY package* ./
RUN npm install

COPY . ./

# NOTE: this should point the static files
ARG VITE_STATIC_HOST=https://nginx:4000
ENV VITE_STATIC_HOST=${VITE_STATIC_HOST}
ENV PORT=${PORT:-8000}
RUN npm run build
CMD npm run preview -- --host --port ${PORT}
