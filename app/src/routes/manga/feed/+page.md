<script>
  import FeedTable from "./FeedTable.svelte";
  export let data;
</script>

# manga feed

{#if data.feed_data}

  <div>
    <FeedTable data={data.feed_data} />
  </div>
{/if}
