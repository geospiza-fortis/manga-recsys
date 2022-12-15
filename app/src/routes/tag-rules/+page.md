<script>
  import Table from "$lib/Table.svelte";
  export let data;
  $: assoc_rules = data.assoc_rules;
  let options = {
    autoColumns: true,
    autoColumnsDefinitions: [
      { field: "antecedent", headerFilter: true },
      { field: "consequent", headerFilter: true },
    ],
    initialSort: [
      { column: "confidence", dir: "desc" },
    ],
    pagination: true,
    paginationSize: 20,
  }
</script>

# tag rules

This table contains [association rules][wikipedia] for tags in the mangadex dataset.
We can use these association rules to find relationships and generate recommendations between tags.

<Table data={assoc_rules} {options} />

## notes

We use the [FPGrowth algorithm in PySpark](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.ml.fpm.FPGrowth.html) to generate the association rules.
We also note relevant terminology sourced from [Wikipedia] below.

### support

Support is an indicator of frequency of a set of tags.

$$
supp(X) = \frac{|(i, t) \in T: X \subseteq t|}{|T|}
$$

where $(i, t)$ is the identifier and itemset of a transaction.

### confidence

Confidence is the percentage of times that a set of tags is present when another set of tags is present.

$$
conf(X \rightarrow Y) = \frac{supp(X \cap Y)}{supp(X)}
$$

where $X \rightarrow Y$ is the rule.

### lift

Lift gives a measure of how likely two sets of tags are independent of each other.
When lift is greater than 1, then the sets are dependent.
When lift is less than 1, then the sets are independent.

$$
lift(X \rightarrow Y) = \frac{conf(X \cap Y)}{supp(X) \times supp(Y)}
$$

[wikipedia]: https://en.wikipedia.org/wiki/Association_rule_learning
