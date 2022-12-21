<script>
  import Fuse from "fuse.js";

  export let data;
  export let table;
  export let headerFilterCol;
  let fuse;
  let headerValue;

  function filterData(headerValue, fuse, data) {
    console.log(fuse, data);
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

  $: fuse = new Fuse(data, { keys: [headerFilterCol], includeScore: true });
  $: table && fuse && table.on("dataFiltering", onDataFilter);
  $: table &&
    data &&
    fuse &&
    table.setData(filterData(headerValue, fuse, data)) &&
    table.setHeaderFilterValue(headerFilterCol, headerValue);
</script>
