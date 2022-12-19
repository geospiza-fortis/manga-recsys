// We generate a psuedo-api for our initial directory structure in GCS. It's
// currently a mess while I play around with different models, and having this
// redirection layer (even at the cost of more requests), allows me to change
// the underlying structure without breaking the front-end.
import { build_path } from "$lib/data.js";
const mapping = {
  "data/manga.parquet": "data/processed/2022-12-10-mangadex-manga.parquet",
  "data/chapter.parquet": "data/processed/2022-12-16-mangadex-chapter.parquet",
  "data/group.parquet": "data/processed/2022-12-17-mangadex-group.parquet",
  "data/manga.ndjson": "data/raw/2022-12-10-mangadex-manga.ndjson",
  "data/chapter.ndjson": "data/raw/2022-12-16-mangadex-chapter.ndjson",
  "data/group.ndjson": "data/raw/2022-12-17-mangadex-group.ndjson",
  "models/tag-rules": "data/processed/2022-12-14-tag-rules",

  // served compressed by default
  metadata: "data/gz/processed/2022-12-17-metadata-listing",
  "models/group-manga": "data/gz/processed/2022-12-18-recommendation-group-manga"
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
