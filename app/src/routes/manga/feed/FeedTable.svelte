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
    removeMangaFromLibrary,
    fetchTagWordVectors,
    computeMeanVector,
    computeTagVector,
    computeVectorSimilarity
  } from "$lib/personalization.js";
  import { browser } from "$app/environment";
  import { marked } from "marked";

  export let data;
  export let paginationSize = 25;
  let processed = [];
  let library = [];

  function computePersonalVector(data, word_vectors) {
    if (data.length == 0) return [];
    if (word_vectors.size == 0) return [];
    let manga_vectors = data.map((row) =>
      computeTagVector(
        row.tags.map((t) => t.name),
        word_vectors
      )
    );
    return computeMeanVector(manga_vectors);
  }

  async function process(data, _) {
    if (!data) return [];
    library = await getLibrary();
    let word_vectors;
    let personal_vector;
    if (library.length == 0) {
      word_vectors = new Map();
      personal_vector = [];
    } else {
      word_vectors = await fetchTagWordVectors();
      personal_vector = computePersonalVector(library, word_vectors);
    }

    let ids = library.map((row) => row.id);
    return data
      .filter((row) => row.tags.length > 0)
      .map((row) => {
        // compute the vector of the current manga
        return {
          ...row,
          inLibrary: ids.includes(row.id),
          similarity:
            personal_vector.length && word_vectors.size
              ? computeVectorSimilarity(
                  personal_vector,
                  computeTagVector(
                    row.tags.map((t) => t.name),
                    word_vectors
                  )
                )
              : 0
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
    initialSort:
      library.length > 0
        ? [{ column: "similarity", dir: "desc" }]
        : [{ column: "updatedAt", dir: "desc" }],
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
        field: "similarity",
        title: "sim",
        // 2 decimal points
        formatter: (cell) => cell.getValue().toFixed(2),
        visible: library.length > 0
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
      let description = row.getData().description;
      if (!description) return;
      tippy(row.getElement(), {
        content: marked(description),
        allowHTML: true
      });
    });
  $: table && table.on("rowMouseOut", (_, row) => destroyTippy(row));
</script>

<Table data={processed} {options} bind:table />
