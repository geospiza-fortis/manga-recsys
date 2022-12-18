export async function load({ fetch }) {
  const base_url = import.meta.env.VITE_STATIC_HOST;
  let get_data = async (suffix) => {
    let url = `${base_url}/data/processed/2022-12-17-metadata-listing/${suffix}`;
    let resp = await fetch(url);
    return await resp.json();
  };

  return {
    group_summary: await get_data("group_summary.json")
  };
}
