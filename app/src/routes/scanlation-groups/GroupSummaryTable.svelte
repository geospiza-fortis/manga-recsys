<script>
  import Table from "$lib/Table.svelte";

  export let data;
  export let selected_group_id = null;
  let table = null;

  let options = {
    autoColumns: true,
    pagination: true,
    paginationSize: 10,
    selectable: 1,
    // sort by manga count descending
    initialSort: [{ column: "manga_count", dir: "desc" }],
    // hide the id column
    autoColumnsDefinitions: [{ field: "group_id", visible: false }]
  };
  $: table &&
    table.on("rowClick", (_, row) => {
      selected_group_id = row.getData().group_id;
    });
</script>

<Table {data} {options} bind:table />
