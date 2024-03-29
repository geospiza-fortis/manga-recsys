async function tag_rule_data(fetch, suffix) {
  let resp = await fetch(`/api/v1/models/tag-rules/${suffix}?server=true`);
  return await resp.json();
}

// This function is mostly vestigial; it takes too long to actually compute the
// force directed layout on the client, so we just use the precomputed layout
// from Gephi.
async function get_vis_network_from_assoc(fetch) {
  let assoc_rules = await tag_rule_data(fetch, "association_rules.json");
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

export async function load({ fetch }) {
  let gephi_assoc = await tag_rule_data(fetch, "gephi_assoc.json");
  return { gephi_assoc };
}
