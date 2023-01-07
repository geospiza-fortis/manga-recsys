<script>
  import FeedTable from "./FeedTable.svelte";
  import PersonalLibraryTable from "$lib/PersonalLibraryTable.svelte";
  import PersonalLibraryChart from "$lib/PersonalLibraryChart.svelte";
  import PolarChart from "$lib/PolarChart.svelte";

  export let data;
  let rowData;
  let group;
  let min_support_step;
  let shared_layout = {
    height: 400
  };
</script>

<h1>manga feed</h1>

<p>
  We use some of the work on building recommendation systems from tags to re-rank most recent
  uploads to MangaDex. Add manga to your library, and it will sort the 100 most recent uploads to
  your preferences.
</p>

<h2>personal library</h2>

<p>
  This contains any manga that you have added to your personal library from the feed. The chart
  shows how similar it is to a set of tags.
</p>

<PersonalLibraryTable paginationSize={10} />

<div class="plots" style="--grid-size={rowData ? 2 : 1}">
  <PersonalLibraryChart
    layout={{ title: `Personal library, similarity to ${group} tags`, ...shared_layout }}
    bind:group
    bind:min_support_step
  />
  {#if rowData}
    <PolarChart
      ref_tags={[rowData.tags.map((t) => t.name)]}
      layout={{
        title: `${rowData.name}, similarity to ${group} tags`,
        ...shared_layout
      }}
      {group}
      {min_support_step}
    />
  {/if}
</div>

<h2>feed</h2>

<p>
  This feed contains recent manga from MangaDex that have a chapter available and has been
  translated into English. It updates at most once every five minutes. Click on a row to compare it
  to your library.
</p>

{#if data.feed_data}
  <div>
    <FeedTable data={data.feed_data} click={(row) => (rowData = row.getData())} />
  </div>
{/if}

<style>
  /** grid the plots side by side if the page is large enough */
  .plots {
    display: grid;
    grid-template-columns: repeat(var(--grid-size, 2), 1fr);
  }
  /** if mobile, then display without the grid */
  @media (max-width: 600px) {
    .plots {
      display: block;
    }
  }
</style>
