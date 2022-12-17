import { invert } from "lodash-es";

export async function load({ fetch }) {
  const base_url = import.meta.env.VITE_STATIC_HOST;
  let tag_rule_data = async (suffix) => {
    let url = `${base_url}/data/processed/2022-12-14-tag-rules/${suffix}`;
    let resp = await fetch(url);
    return await resp.json();
  };

  let assoc_rules = await tag_rule_data("association_rules.json");
  // lets generate nodes and edges for our network
  let node_labels = new Set(
    assoc_rules.flatMap((rule) => [rule.antecedent.join(", "), rule.consequent.join(", ")])
  );
  // give each node a unique id
  let node_map = new Map([...node_labels].map((label, i) => [label, i]));
  let nodes = Array(...node_map.entries()).map(([label, id]) => {
    return { id, label };
  });
  let edges = assoc_rules.map((rule) => {
    return {
      from: node_map.get(rule.antecedent.join(", ")),
      to: node_map.get(rule.consequent.join(", "))
    };
  });
  return { nodes, edges };
}
