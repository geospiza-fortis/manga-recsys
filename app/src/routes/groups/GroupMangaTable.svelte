<script>
  import Table from "$lib/Table.svelte";
  import { tippyMangaInfo, destroyTippy } from "$lib/tabulator.js";

  async function get_group_manga(group_id) {
    let resp = await fetch(`/api/v1/metadata/group_manga/${group_id}.json`);
    return await resp.json();
  }

  export let group_id;
  let table;

  let data;
  let options = {
    autoColumns: true,
    pagination: true,
    paginationSize: 10,
    paginationCounter: "rows",
    autoColumnsDefinitions: [
      // hide ids and group
      { field: "manga_id", visible: false },
      { field: "group_id", visible: false },
      { field: "group_name", visible: false },
      {
        field: "manga_name",
        formatter: "link",
        formatterParams: {
          urlPrefix: "https://mangadex.org/title/",
          labelField: "manga_name",
          urlField: "manga_id",
          target: "_blank"
        }
      }
    ],
    initialSort: [{ column: "chapter_count", dir: "desc" }]
  };
  $: table && table.on("rowMouseOver", (_, row) => tippyMangaInfo(row, { placement: "bottom" }));
  $: table && table.on("rowMouseOut", (_, row) => destroyTippy(row));

  $: group_id && get_group_manga(group_id).then((r) => (data = r));
</script>

<Table {data} {options} bind:table />
