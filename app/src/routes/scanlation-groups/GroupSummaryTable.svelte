<script>
  import Table from "$lib/Table.svelte";
  import { tippyGroupInfo, destroyTippy } from "$lib/tabulator.js";
  import TableFuseHeaderFilter from "$lib/TableFuseHeaderFilter.svelte";

  export let data;
  export let selected_group_id;
  let table;

  $: options = {
    autoColumns: true,
    pagination: true,
    paginationSize: 10,
    paginationCounter: "rows",
    selectable: 1,
    initialSort: [{ column: "manga_count", dir: "desc" }],
    autoColumnsDefinitions: [
      { field: "group_id", visible: false },
      {
        field: "group_name",
        headerFilter: true,
        // no-op function since we're going to filter the data ourselves
        headerFilterFunc: () => true,
        formatter: "link",
        formatterParams: {
          urlPrefix: "https://mangadex.org/group/",
          labelField: "group_name",
          urlField: "group_id",
          target: "_blank"
        }
      }
    ]
  };

  // when hovering over a row, show the tooltip with the group info
  $: table && table.on("rowMouseOver", (_, row) => tippyGroupInfo(row, { placement: "bottom" }));
  $: table && table.on("rowMouseOut", (_, row) => destroyTippy(row));
  $: table && table.on("rowClick", (_, row) => (selected_group_id = row.getData().group_id));
</script>

<Table {data} {options} bind:table />
<TableFuseHeaderFilter {data} {table} {options} headerFilterCol={"group_name"} />
