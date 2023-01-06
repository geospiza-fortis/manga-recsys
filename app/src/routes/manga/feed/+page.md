<script>
  import FeedTable from "./FeedTable.svelte";
  import PersonalLibraryTable from "$lib/PersonalLibraryTable.svelte";

  export let data;
</script>

# manga feed

## personal library

<PersonalLibraryTable paginationSize={10} />

## feed

{#if data.feed_data}

  <div>
    <FeedTable data={data.feed_data} />
  </div>
{/if}
