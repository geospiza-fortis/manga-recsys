<script>
  import FeedTable from "./FeedTable.svelte";
  import PersonalLibraryTable from "$lib/PersonalLibraryTable.svelte";
  import PersonalLibraryChart from "$lib/PersonalLibraryChart.svelte";

  export let data;
</script>

# manga feed

## personal library

<div class="personal">
<div>
<PersonalLibraryTable paginationSize={10} />
</div>
<div>
<PersonalLibraryChart />
</div>
</div>

## feed

{#if data.feed_data}

  <div>
    <FeedTable data={data.feed_data} />
  </div>
{/if}

<style>
  .personal {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
  @media (max-width: 600px) {
    .personal {
      display: flex;
      flex-direction: column;
    }
  }
</style>
