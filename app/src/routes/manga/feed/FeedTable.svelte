<script>
  import Table from "$lib/Table.svelte";
  import { destroyTippy } from "$lib/tabulator.js";
  import tippy from "tippy.js";
  import "tippy.js/dist/tippy.css";
  import { DateTime } from "luxon";
  import {
    library_edits,
    getLibrary,
    addMangaToLibrary,
    removeMangaFromLibrary
  } from "$lib/personalization.js";
  import { browser } from "$app/environment";

  export let data;
  export let paginationSize = 25;
  let processed = [];

  async function process(data, _) {
    if (!data) return [];
    let library = await getLibrary();
    let ids = library.map((row) => row.id);
    return data.map((row) => {
      return {
        ...row,
        inLibrary: ids.includes(row.id)
      };
    });
  }

  $: browser &&
    process(data, $library_edits).then((d) => {
      processed = d;
    });

  let table;

  $: options = {
    pagination: true,
    paginationSize: paginationSize,
    paginationCounter: "rows",
    columns: [
      // checkbox element that will add or remove manga from the library
      {
        field: "inLibrary",
        title: "added",
        formatter: "tickCross",
        editor: true,
        hozAlign: "center"
      },
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
        title: "tags",
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
      }
    ]
  };

  $: table &&
    table.on("cellEdited", async (cell) => {
      const rowData = cell.getRow().getData();
      let value = rowData.inLibrary;
      if (value) {
        await addMangaToLibrary(rowData.id, rowData.name, rowData.tags);
      } else {
        await removeMangaFromLibrary(rowData.id);
      }
      // also, we need to trigger the component to update
      $library_edits += 1;
    });
  // when hovering over a row, show the tooltip with the group info
  $: table &&
    table.on("rowMouseOver", (_, row) => {
      tippy(row.getElement(), { content: row.getData().description });
    });
  $: table && table.on("rowMouseOut", (_, row) => destroyTippy(row));
</script>

<Table data={processed} {options} bind:table />
