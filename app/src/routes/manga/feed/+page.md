<script>
  import FeedTable from "./FeedTable.svelte";
  import PersonalLibraryTable from "$lib/PersonalLibraryTable.svelte";
  import PersonalLibraryChart from "$lib/PersonalLibraryChart.svelte";

  export let data;
</script>

# manga feed

We use some of the work on building recommendation systems from tags to re-rank most recent uploads to MangaDex.
Add manga to your library, and it will sort the 100 most recent uploads to your preferences.

## personal library

This contains any manga that you have added to your personal library from the feed.
The chart shows how similar it is to a set of tags.

<div class="personal">
<div>
<PersonalLibraryTable paginationSize={10} />
</div>
<div>
<PersonalLibraryChart />
</div>
</div>

## feed

This feed contains recent manga from MangaDex that have a chapter available and has been translated into English.
It updates at most once every five minutes.

{#if data.feed_data}

  <div>
    <FeedTable data={data.feed_data} />
  </div>
{/if}

<style>
  /* .personal {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
  @media (max-width: 600px) {
    .personal {
      display: flex;
      flex-direction: column;
    }
  } */
</style>
