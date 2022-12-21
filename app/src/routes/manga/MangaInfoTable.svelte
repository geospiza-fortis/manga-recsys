<script>
  import Table from "$lib/Table.svelte";
  import { tippyMangaInfo, destroyTippy } from "$lib/tabulator.js";
  import Fuse from "fuse.js";

  export let data;
  export let selected_id;

  let table;
  let fuse;

  let headerValue;

  $: options = {
    autoColumns: true,
    pagination: true,
    paginationSize: 10,
    paginationCounter: "rows",
    selectable: 1,
    initialSort: [
      { column: "score", dir: "asc" }
      // TODO: initial sort with two columns is broken
      // { column: "manga_count", dir: "desc" }
    ],
    autoColumnsDefinitions: [
      { field: "id", visible: false },
      {
        field: "name",
        headerFilter: true,
        // no-op function since we're going to filter the data ourselves
        headerFilterFunc: () => true,
        formatter: "link",
        formatterParams: {
          urlPrefix: "https://mangadex.org/manga/",
          labelField: "name",
          urlField: "id",
          target: "_blank"
        }
      }
    ],
    initialHeaderFilter: [{ field: "name", value: headerValue }]
  };

  // return scores
  $: data && (fuse = new Fuse(data, { keys: ["name"], includeScore: true }));
  // when hovering over a row, show the tooltip with the group info
  $: table &&
    table.on("rowMouseOver", (_, row) => tippyMangaInfo(row, { placement: "bottom" }, "id"));
  $: table && table.on("rowMouseOut", (_, row) => destroyTippy(row));
  $: table &&
    table.on("rowClick", (_, row) => {
      selected_id = row.getData().id;
    });
  $: table &&
    fuse &&
    table.on("dataFiltering", (filters) => {
      // get the header filter for group name
      const groupFilter = filters.find((f) => f.field === "name");
      // get the value from the header filter
      headerValue = groupFilter ? groupFilter.value : null;
    });
  $: filteredData =
    headerValue && headerValue.length > 0
      ? fuse.search(headerValue).map((r) => ({ ...r.item, score: r.score }))
      : data.map((r) => ({ ...r, score: 1 / r.chapter_count }));
</script>

<Table data={filteredData} {options} bind:table />
