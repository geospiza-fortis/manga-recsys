<script>
  import Table from "$lib/Table.svelte";
  import tippy from "tippy.js";
  import "tippy.js/dist/tippy.css";

  export let data;
  let options = {
    autoColumns: true,
    pagination: true,
    paginationSize: 20
  };
  let table = null;

  // set callback on mouseover on the row
  $: table &&
    table.on("rowMouseOver", (e, row) => {
      // get group_id from row
      let group_id = row.getData().group_id;
      console.log("group_id", group_id);
      let element = row.getElement();

      // now let's add a tooltip using tippy
      tippy(element, {
        // add an iframe to the mangadex page
        content: "<iframe src='https://mangadex.org/group/" + group_id + "'></iframe>",
        allowHTML: true
      });
    });
</script>

<Table {data} {options} bind:table />
