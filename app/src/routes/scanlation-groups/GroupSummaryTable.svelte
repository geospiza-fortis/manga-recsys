<script>
  import Table from "$lib/Table.svelte";
  import Fuse from "fuse.js";

  export let data;
  export let selected_group_id;
  let table;
  let fuse;

  let filtered_group_ids = new Set(data.map((r) => r.group_id));
  $: console.log(filtered_group_ids);

  // custom header search: https://tabulator.info/docs/5.4/filter#func-custom
  let options = {
    autoColumns: true,
    pagination: true,
    paginationSize: 10,
    selectable: 1,
    // sort by manga count descending
    initialSort: [{ column: "manga_count", dir: "desc" }],
    // hide the id column
    autoColumnsDefinitions: [
      { field: "group_id", visible: false },
      {
        field: "group_name",
        headerFilter: true,
        headerFilterFunc: (headerValue, rowValue, rowData, filterParams) =>
          filtered_group_ids.has(rowData.group_id)
      }
    ]
  };
  // return scores
  $: data && (fuse = new Fuse(data, { keys: ["group_name"], includeScore: true }));
  $: table &&
    table.on("rowClick", (_, row) => {
      selected_group_id = row.getData().group_id;
    });
  $: table &&
    fuse &&
    table.on("dataFiltering", (filters) => {
      // get the header filter for group name
      const group_name_filter = filters.find((f) => f.field === "group_name");
      // get the value from the header filter
      if (!group_name_filter) return;
      let search = fuse.search(group_name_filter.value);
      console.log(search);
      filtered_group_ids = new Set(search.map((r) => r.item.group_id));
    });
</script>

<Table {data} {options} bind:table />
