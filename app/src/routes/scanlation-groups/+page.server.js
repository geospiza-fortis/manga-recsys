import { fetch_data } from "$lib/data.js";

export async function load({ fetch }) {
  return {
    group_summary: await fetch_data({
      fetch,
      path: "/data/processed/2022-12-17-metadata-listing/group_summary.json"
    })
  };
}
