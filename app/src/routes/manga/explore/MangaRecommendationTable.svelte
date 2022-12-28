<script>
  import Table from "$lib/Table.svelte";
  import { tippyMangaInfo, destroyTippy } from "$lib/tabulator.js";

  async function get_manga_recommendation(uid, model) {
    let resp = await fetch(`/api/v1/models/${model}/recommendations/${uid}.json`);
    return await resp.json();
  }

  export let selected_id;
  export let model = "manga-tags-word2vec";
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
  $: selected_id && get_manga_recommendation(selected_id, model).then((r) => (data = r));
</script>

<Table {data} {options} bind:table />
