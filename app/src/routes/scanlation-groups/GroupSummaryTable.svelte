<script>
  import Table from "$lib/Table.svelte";
  import { tippyGroupInfo, destroyTippy } from "$lib/tabulator.js";
  import Fuse from "fuse.js";

  // NOTE: this code is awful, but it gets the job done. We basically hook into
  // the header filter to get the value of the filter, and then generate a new
  // set of data. We then recreate the table with the new data. This is bad
  // because we are creating a new table every time the data changes, which is
  // not ideal. Instead, we should be able to update the data in the table. This
  // is doable, but it's more effort than I want to expend right now.

  export let data;
  export let selected_group_id;
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
      },
      // hide score column
      { field: "score", visible: false }
    ],
    initialHeaderFilter: [{ field: "group_name", value: headerValue }]
  };

  // return scores
  $: data && (fuse = new Fuse(data, { keys: ["group_name"], includeScore: true }));
  // when hovering over a row, show the tooltip with the group info
  $: table && table.on("rowMouseOver", (_, row) => tippyGroupInfo(row, { placement: "bottom" }));
  $: table && table.on("rowMouseOut", (_, row) => destroyTippy(row));
  $: table &&
    table.on("rowClick", (_, row) => {
      selected_group_id = row.getData().group_id;
    });
  $: table &&
    fuse &&
    table.on("dataFiltering", (filters) => {
      // get the header filter for group name
      const groupFilter = filters.find((f) => f.field === "group_name");
      // get the value from the header filter
      headerValue = groupFilter ? groupFilter.value : null;
    });
  $: filteredData =
    headerValue && headerValue.length > 0
      ? fuse.search(headerValue).map((r) => ({ ...r.item, score: r.score }))
      : data.map((r) => ({ ...r, score: 1 / r.manga_count }));
</script>

<Table data={filteredData} {options} bind:table />
