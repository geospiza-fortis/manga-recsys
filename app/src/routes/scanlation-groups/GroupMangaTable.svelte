<script>
  import Table from "$lib/Table.svelte";
  import { fetch_data } from "$lib/data.js";

  async function get_group_manga(group_id) {
    return await fetch_data({
      fetch,
      path: `data/processed/2022-12-17-metadata-listing/group_manga/${group_id}.json`
    });
  }

  export let group_id;

  let data;
  let options = {
    autoColumns: true,
    pagination: true,
    paginationSize: 10,
    paginationCounter: "rows",
    autoColumnsDefinitions: [
      { field: "manga_id", visible: false },
      { field: "group_id", visible: false }
    ],
    initialSort: [{ column: "chapter_count", dir: "desc" }]
  };

  $: group_id && get_group_manga(group_id).then((d) => (data = [...d]));
</script>

<Table {data} {options} />
