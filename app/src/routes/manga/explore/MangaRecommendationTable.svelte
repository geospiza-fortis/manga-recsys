<script>
  import Table from "$lib/Table.svelte";
  import { tippyMangaInfo, destroyTippy } from "$lib/tabulator.js";

  async function get_manga_recommendation(uid) {
    let resp = await fetch(`/api/v1/models/manga-tags-word2vec/recommendations/${uid}.json`);
    return await resp.json();
  }

  function fill_in_rec_name(data) {
    return data.map((r) => {
      r.rec_name = r.rec_name || r.rec_id;
      return r;
    });
  }

  export let selected_id;
  let table;

  let data;
  let options = {
    autoColumns: true,
    pagination: true,
    paginationSize: 10,
    paginationCounter: "rows",
    autoColumnsDefinitions: [
      // hide id and name
      { field: "id", visible: false },
      { field: "name", visible: false },
      { field: "rec_id", visible: false },
      {
        title: "recommendation",
        field: "rec_name",
        formatter: "link",
        formatterParams: {
          urlPrefix: "https://mangadex.org/title/",
          labelField: "rec_name",
          urlField: "rec_id",
          target: "_blank"
        }
      }
    ],
    initialSort: [{ column: "distance", dir: "asc" }]
  };
  $: table &&
    table.on("rowMouseOver", (_, row) => tippyMangaInfo(row, { placement: "bottom" }, "rec_id"));
  $: table && table.on("rowMouseOut", (_, row) => destroyTippy(row));
  $: selected_id && get_manga_recommendation(selected_id).then((r) => (data = fill_in_rec_name(r)));
</script>

<Table {data} {options} bind:table />
