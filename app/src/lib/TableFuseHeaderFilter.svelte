<script>
  import Fuse from "fuse.js";

  export let data;
  export let table;
  export let headerFilterCol;
  export let options = {};
  let fuse;
  let headerValue;

  function filterData(headerValue, fuse, data) {
    if (headerValue && headerValue.length > 0) {
      return fuse.search(headerValue).map((r) => ({ ...r.item, search_relevance: r.score }));
    } else {
      return data.map((r) => ({ ...r, search_relevance: 1 }));
    }
  }

  function onDataFilter(filters) {
    const headerFilter = filters.find((f) => f.field === headerFilterCol);
    headerValue = headerFilter ? headerFilter.value : null;
  }

  function triggerUpdate(table, options, headerFilterCol, headerValue, fuse, data) {
    table.setData(filterData(headerValue, fuse, data));
    table.setHeaderFilterValue(headerFilterCol, headerValue);

    // delay sorting by 100ms to allow the data to be updated
    setTimeout(() => {
      if (headerValue && headerValue.length > 0) {
        console.log("setting search relevance sort");
        table.setSort("search_relevance", "asc");
        return;
      }
      if (options.initialSort) {
        table.setSort(options.initialSort);
        return;
      }
      // otherwise clear sort
      table.clearSort();
    }, 100);
  }

  $: fuse = new Fuse(data, { keys: [headerFilterCol], includeScore: true });
  $: table && fuse && table.on("dataFiltering", onDataFilter);
  $: table &&
    data &&
    fuse &&
    triggerUpdate(table, options, headerFilterCol, headerValue, fuse, data);
</script>
