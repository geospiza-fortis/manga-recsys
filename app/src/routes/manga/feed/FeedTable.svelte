<script>
  import Table from "$lib/Table.svelte";
  import { destroyTippy } from "$lib/tabulator.js";
  import tippy from "tippy.js";
  import "tippy.js/dist/tippy.css";
  import { DateTime } from "luxon";

  export let data;

  let table;

  $: options = {
    autoColumns: true,
    pagination: true,
    paginationSize: 50,
    paginationCounter: "rows",
    autoColumnsDefinitions: [
      {
        field: "updatedAt",
        title: "updated",
        formatter: (cell) => {
          const rowData = cell.getRow().getData();
          // format using luxon and give relative time
          return DateTime.fromISO(rowData.updatedAt).toRelative();
        }
      },
      {
        field: "originalLanguage",
        title: "lang"
      },
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
        },
        width: 300
      },
      {
        field: "latestUploadedChapter",
        title: "chapter",
        formatter: "link",
        formatterParams: {
          urlPrefix: "https://mangadex.org/chapter/",
          label: (cell) => (cell.getValue() ? "link" : ""),
          target: "_blank"
        }
      },
      {
        field: "tags",
        // custom formatter to flatten object
        formatter: (cell) => {
          const rowData = cell.getRow().getData();
          return rowData.tags.map((tag) => tag.name).join(", ");
        },
        // also set max width
        width: 200
      },
      {
        field: "availableTranslatedLanguages",
        title: "translated"
      },
      {
        field: "description",
        visible: false
      }
    ]
  };

  // when hovering over a row, show the tooltip with the group info
  $: table &&
    table.on("rowMouseOver", (_, row) => {
      tippy(row.getElement(), { content: row.getData().description });
    });
  $: table && table.on("rowMouseOut", (_, row) => destroyTippy(row));
</script>

<Table {data} {options} bind:table />
