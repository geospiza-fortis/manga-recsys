<script>
  import Table from "$lib/Table.svelte";
  import { tippyMangaInfo, destroyTippy } from "$lib/tabulator.js";
  import "tippy.js/dist/tippy.css";
  import { library_edits, getLibrary, removeMangaFromLibrary } from "$lib/personalization.js";
  import { browser } from "$app/environment";
  import { onMount } from "svelte";
  import { DateTime } from "luxon";

  export let data = [];
  export let paginationSize = 10;

  let table;

  onMount(() => {
    $library_edits += 1;
  });

  $: browser &&
    $library_edits &&
    getLibrary().then((library) => {
      data = library;
      $library_edits = 0;
    });

  $: options = {
    pagination: true,
    paginationSize: paginationSize,
    paginationCounter: "rows",
    columns: [
      {
        field: "added",
        formatter: (cell) => {
          const rowData = cell.getRow().getData();
          // format using luxon and give relative time
          return DateTime.fromISO(rowData.added).toRelative();
        }
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
        width: 100
      },
      {
        field: "remove",
        title: "remove",
        formatter: "tickCross",
        hozAlign: "center",
        editor: true
      }
    ]
  };

  $: table &&
    table.on("cellEdited", async (cell) => {
      const rowData = cell.getRow().getData();
      await removeMangaFromLibrary(rowData.id);
      // also, we need to trigger the component to update
      $library_edits += 1;
    });
  // when hovering over a row, show the tooltip with the group info
  $: table && table.on("rowMouseOver", (_, row) => tippyMangaInfo(row, {}, "id"));
  $: table && table.on("rowMouseOut", (_, row) => destroyTippy(row));
</script>

{#if data.length}
  <Table {data} {options} bind:table />
{:else}
  <p>No manga in personal library.</p>
{/if}
