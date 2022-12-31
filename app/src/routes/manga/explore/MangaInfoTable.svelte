<script>
  import Table from "$lib/Table.svelte";
  import TableFuseHeaderFilter from "$lib/TableFuseHeaderFilter.svelte";
  import { tippyMangaInfo, destroyTippy } from "$lib/tabulator.js";

  export let data;
  export let selected_id;

  let table;

  $: options = {
    autoColumns: true,
    pagination: true,
    paginationSize: 10,
    paginationCounter: "rows",
    selectable: 1,
    initialSort: [{ column: "chapter_count", dir: "desc" }],
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
          // get row from cell
          label: (cell) => {
            const rowData = cell.getRow().getData();
            return rowData.name || rowData.id;
          },
          urlField: "id",
          target: "_blank"
        }
      }
    ]
  };

  // when hovering over a row, show the tooltip with the group info
  $: table && table.on("rowMouseOver", (_, row) => tippyMangaInfo(row, {}, "id"));
  $: table && table.on("rowMouseOut", (_, row) => destroyTippy(row));
  $: table && table.on("rowClick", (_, row) => (selected_id = row.getData().id));
</script>

<Table {data} {options} bind:table />
<TableFuseHeaderFilter {data} {table} {options} headerFilterCol={"name"} />
