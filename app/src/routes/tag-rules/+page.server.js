export async function load({ fetch }) {
  let tag_rule_data = async (suffix) => {
    let resp = await fetch(`/api/v1/models/tag-rules/${suffix}?server=true`);
    return await resp.json();
  };

  return {
    assoc_rules: await tag_rule_data("association_rules.json")
  };
}
