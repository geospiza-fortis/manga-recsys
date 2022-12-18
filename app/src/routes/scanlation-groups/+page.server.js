export async function load({ fetch }) {
  let resp = await fetch(`/api/v1/metadata/group_summary.json?server=true`);
  return {
    group_summary: await resp.json()
  };
}
