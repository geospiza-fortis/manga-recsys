// We generate a psuedo-api for our initial directory structure in GCS. It's
// currently a mess while I play around with different models, and having this
// redirection layer (even at the cost of more requests), allows me to change
// the underlying structure without breaking the front-end.
import { browser, dev } from "$app/environment";

export function build_path(path, client = false) {
  let base_url = import.meta.env.VITE_STATIC_HOST;
  // get current port
  // Replace nginx with localhost if we're running in the browser and in
  // development mode. This assumes that we're running via the docker compose
  // setup.
  if ((browser && dev) || client) {
    base_url = base_url.replace("nginx", "localhost");
  }
  return `${base_url}/${path}`;
}

const mapping = {
  "data/manga.parquet": "data/processed/2022-12-10-mangadex-manga.parquet",
  "data/chapter.parquet": "data/processed/2022-12-16-mangadex-chapter.parquet",
  "data/group.parquet": "data/processed/2022-12-17-mangadex-group.parquet",
  "data/manga.ndjson": "data/raw/2022-12-10-mangadex-manga.ndjson",
  "data/chapter.ndjson": "data/raw/2022-12-16-mangadex-chapter.ndjson",
  "data/group.ndjson": "data/raw/2022-12-17-mangadex-group.ndjson",

  // plots that are "static", probably should rename the data path in the future
  "data/manga-tags-plots": "data/processed/2022-12-27-recommendation-manga-plots",

  // tag rules are a type of model
  "models/tag-rules": "data/processed/2022-12-14-tag-rules",

  // served compressed by default
  metadata: "data/gz/processed/2022-12-17-metadata-listing",
  // v1: data/gz/processed/2022-12-18-recommendation-group-manga
  "models/group-manga": "data/gz/processed/2022-12-19-recommendation-group-manga",
  "models/manga-tags-word2vec": "data/gz/processed/2022-12-20-recommendation-manga-tags-word2vec",
  "models/manga-tags-lsi": "data/gz/processed/2022-12-27-recommendation-manga-tags-lsi"
};

export async function GET({ url, params, fetch }) {
  // check for client url parameter set
  let server = url.searchParams.get("server") === "true";
  let { slug } = params;

  // check if the key is a substring of the slug and replace it with our value
  for (let [key, value] of Object.entries(mapping)) {
    if (slug.includes(key)) {
      slug = slug.replace(key, value);
      break;
    }
  }
  // get decompressed version if we're on server
  if (server) {
    slug = slug.replace("/gz/", "/");
  }

  let redirect_url = build_path(slug, !server);
  if (server) {
    // We just proxy the result, although gross, should be fairly cheap. NOTE:
    // we do _NOT_ want to proxy any static data that are served directly to the
    // client, because that's a waste of effort for the container.
    return await fetch(redirect_url);
  } else {
    return Response.redirect(redirect_url, 302);
  }
}
