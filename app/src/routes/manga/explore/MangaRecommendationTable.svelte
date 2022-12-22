<script>
  import Table from "$lib/Table.svelte";
  import { tippyMangaInfo, destroyTippy } from "$lib/tabulator.js";

  async function get_manga_recommendation(uid) {
    let resp = await fetch(`/api/v1/models/manga-tags-word2vec/recommendations/${uid}.json`);
    return await resp.json();
  }

  export let selected_id;
  let table;

  let data;
  let options = {
    pagination: true,
    paginationSize: 10,
    paginationCounter: "rows",
    columns: [
      {
        title: "recommendation",
        field: "rec_name",
        formatter: "link",
        formatterParams: {
          urlPrefix: "https://mangadex.org/title/",
          label: (cell) => {
            const rowData = cell.getRow().getData();
            return rowData.rec_name || rowData.rec_id;
          },
          urlField: "rec_id",
          target: "_blank"
        }
      },
      { title: "distance", field: "distance" }
    ],
    initialSort: [{ column: "distance", dir: "asc" }]
  };
  $: table &&
    table.on("rowMouseOver", (_, row) => tippyMangaInfo(row, { placement: "bottom" }, "rec_id"));
  $: table && table.on("rowMouseOut", (_, row) => destroyTippy(row));
  $: selected_id && get_manga_recommendation(selected_id).then((r) => (data = r));
</script>

<Table {data} {options} bind:table />
