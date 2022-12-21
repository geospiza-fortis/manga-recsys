<script>
  import Table from "$lib/Table.svelte";
  import { tippyMangaInfo, destroyTippy } from "$lib/tabulator.js";

  async function get_group_manga_recommendation(group_id) {
    let resp = await fetch(`/api/v1/models/group-manga/recommendations/${group_id}.json`);
    return await resp.json();
  }

  export let group_id;
  let table;

  let data;
  let options = {
    pagination: true,
    paginationSize: 10,
    paginationCounter: "rows",
    columns: [
      {
        title: "manga",
        field: "manga_name",
        formatter: "link",
        formatterParams: {
          urlPrefix: "https://mangadex.org/title/",
          labelField: "manga_name",
          urlField: "manga_id",
          target: "_blank"
        }
      },
      { title: "rating", field: "rating" }
    ],
    initialSort: [{ column: "rating", dir: "desc" }]
  };
  $: table && table.on("rowMouseOver", (_, row) => tippyMangaInfo(row, { placement: "bottom" }));
  $: table && table.on("rowMouseOut", (_, row) => destroyTippy(row));
  $: group_id && get_group_manga_recommendation(group_id).then((r) => (data = r));
</script>

<Table {data} {options} bind:table />
