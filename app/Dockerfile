FROM node:18

WORKDIR /app
COPY package* ./
RUN npm install

COPY . ./
CMD npm run dev
