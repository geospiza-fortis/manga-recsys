<script>
  import Table from "$lib/Table.svelte";
  export let data;
  let options = {
    autoColumns: true,
    pagination: true,
    paginationSize: 20,
  }
</script>

# scanlation groups

A scanlation group is a group of people who translate manga into their own language.

<Table data={data.group_summary} {options} />
