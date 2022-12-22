# manga-recsys webapp

This contains all of the webapp code for the manga-recsys project.
Use the `docker compose` command to run this in development, to take advantage of content servicing by nginx.

## quickstart

### development server

Set up a `.env` file with the following variables:

```bash
VITE_STATIC_HOST=https://storage.googleapis.com/manga-recsys
# NOTE: http://localhost:4000 for local development with docker compose
```

Install dependencies using `npm install` and start a development server:

```bash
npm run dev
```

### production build

```bash
npm run build
```

You can preview the production build with `npm run preview`.
