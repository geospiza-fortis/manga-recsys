<script>
  import MangaRecommendationTable from "./MangaRecommendationTable.svelte";
  export let selected_id = null;
  const models = [
    "manga-tags-lsi",
    "manga-tags-word2vec",
    "manga-tags-network-euclidean",
    "manga-tags-network-cosine",
    "manga-tags-network-adj-cosine"
  ];
  let visible_models = models.map((_) => true);
  let column_size = 3;
</script>

<div class="selectors">
  <div>
    <b>visible models</b>
    {#each models as model, i}
      <label>
        <input type="checkbox" bind:checked={visible_models[i]} />
        {model.replace("manga-tags-", "")}
      </label>
    {/each}
  </div>
  <div>
    <b>models per row</b>
    {#each [2, 3] as size}
      <label>
        <input type="radio" name="column_size" value={size} bind:group={column_size} />
        {size}
      </label>
    {/each}
  </div>
</div>

<div class="container" style="--grid-size:{column_size}">
  {#if selected_id}
    {#each models as model, i}
      {#if visible_models[i]}
        <div class="item">
          <h2>{model.replace("manga-tags-", "")}</h2>
          <MangaRecommendationTable {selected_id} {model} />
        </div>
      {/if}
    {/each}
  {/if}
</div>

<style>
  .selectors div {
    border: 1px solid black;
    margin: 1px;
  }

  .container {
    display: grid;
    grid-template-columns: repeat(var(--grid-size, 2), 1fr);
    /** some padding */
    grid-gap: 0.5rem;
  }
  .item {
    overflow: hidden;
  }
</style>
