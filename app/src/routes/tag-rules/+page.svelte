<script>
  import Table from "$lib/Table.svelte";
  export let data;
  $: assoc_rules = data.assoc_rules;
</script>

<h1>tag rules</h1>

<Table data={assoc_rules} options={{ autoColumns: true }} />
