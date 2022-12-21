export async function load({ fetch }) {
  let resp = await fetch(`/api/v1/metadata/manga_info_slim.json?server=true`);
  return {
    manga_info: await resp.json()
  };
}
