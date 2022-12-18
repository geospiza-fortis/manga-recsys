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
