export async function load({ fetch }) {
  const base_url = import.meta.env.VITE_STATIC_HOST;
  let tag_rule_data = async (suffix) => {
    let url = `${base_url}/data/processed/2022-12-14-tag-rules/${suffix}`;
    let resp = await fetch(url);
    return await resp.json();
  };

  return {
    assoc_rules: await tag_rule_data("association_rules.json"),
    freq_itemsets: await tag_rule_data("freq_itemsets.json")
  };
}
