import { browser, dev } from "$app/environment";

export async function fetch_data({ fetch, path }) {
  let base_url = import.meta.env.VITE_STATIC_HOST;
  // Replace nginx with localhost if we're running in the browser and in
  // development mode. This assumes that we're running via the docker compose
  // setup.
  if (browser && dev) {
    base_url = base_url.replace("nginx", "localhost");
  }
  let url = `${base_url}/${path}`;
  let resp = await fetch(url);
  return await resp.json();
}
