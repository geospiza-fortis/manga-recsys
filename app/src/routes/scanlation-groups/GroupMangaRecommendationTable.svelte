<script>
  import Table from "$lib/Table.svelte";

  async function get_group_manga_recommendation(group_id) {
    let resp = await fetch(`/api/v1/models/group-manga/recommendations/${group_id}.json`);
    return await resp.json();
  }

  export let group_id;

  let data;
  let options = {
    pagination: true,
    paginationSize: 10,
    paginationCounter: "rows",
    columns: [
      { field: "group_id", visible: false },
      { field: "group_name" },
      { field: "manga_id", visible: false },
      { field: "manga_name" },
      { field: "rating" }
    ],
    initialSort: [{ column: "rating", dir: "desc" }]
  };

  $: group_id && get_group_manga_recommendation(group_id).then((r) => (data = [...r]));
</script>

<Table {data} {options} />
