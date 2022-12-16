FROM node:18

WORKDIR /app
COPY package* ./
RUN npm install

COPY . ./

ENV PORT=${PORT:-8000}
RUN npm run build
CMD npm run preview -- --host --port ${PORT}
