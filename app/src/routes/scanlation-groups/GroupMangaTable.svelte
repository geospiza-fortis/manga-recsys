<script>
  import Table from "$lib/Table.svelte";

  async function get_group_manga(group_id) {
    let resp = await fetch(`/api/v1/metadata/group_manga/${group_id}.json`);
    return await resp.json();
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

  $: group_id && get_group_manga(group_id).then((r) => (data = [...r]));
</script>

<Table {data} {options} />
