<script>
  import { onMount } from "svelte";

  async function fetchManifest() {
    let resp = await fetch("/api/v1/data/manga-tags-plots/manifest.json");
    return await resp.json();
  }

  function convertManifest(manifest) {
    // we convert this into a nested dictionary of model -> group -> tag -> list[reducer]
    // so that we can easily access the reducer for a given model, group, and tag
    // NOTE: what awful code, who could have possibly written this?
    let result = {};
    for (let row of manifest) {
      let { model, group, tag, reducer } = row;
      if (!(model in result)) {
        result[model] = {};
      }
      if (!(group in result[model])) {
        result[model][group] = {};
      }
      // the tag is a list of reducers
      if (!(tag in result[model][group])) {
        result[model][group][tag] = [];
      }
      result[model][group][tag].push(reducer);
    }
    return result;
  }

  function buildPlotUrl(model, group, tag, reducer) {
    return `/api/v1/data/manga-tags-plots/${model}/${group}/${tag}/${reducer}.png`;
  }

  let manifest;
  let selectedGroup = "genre";
  let selectedTag = selectedGroup == "genre" ? "Isekai" : "Reincarnation";
  let selectedReducer = "UMAP";

  let visible_plots = [];
  let column_size = 3;

  onMount(async () => {
    manifest = convertManifest(await fetchManifest());
  });

  function mergeModelNames(fixed, manifest) {
    let manifestModels = manifest ? Object.keys(manifest) : [];
    let res = [...fixed];
    for (let model of manifestModels) {
      if (!res.includes(model)) {
        res.push(model);
      }
    }
    return res;
  }

  // get the set of models
  $: models = mergeModelNames(
    ["lsi", "word2vec", "network-euclidean", "network-cosine", "network-adj-cosine"],
    manifest
  );
  $: visible_plots = visible_plots.length > 0 ? visible_plots : models.map((_) => true);

  // get the set of groups
  $: groups = manifest && models ? Object.keys(manifest[models[0]]) : [];
  // now get the set of tags, which are the same for each model and group
  $: tags = manifest && models && groups ? Object.keys(manifest[models[0]][selectedGroup]) : [];
  // get the set of reducers, which are the same for each model, group, and tag
  $: reducers =
    manifest && models && groups && tags ? manifest[models[0]][selectedGroup][tags[0]] : [];
</script>

<!-- create a radio button for each choice, separated by a div -->
<div class="selectors">
  <div>
    {#each groups as group}
      <label>
        <input
          type="radio"
          name="group"
          value={group}
          bind:group={selectedGroup}
          on:change={() => (selectedTag = selectedGroup == "genre" ? "Isekai" : "Reincarnation")}
        />
        {group}
      </label>
    {/each}
  </div>
  <div>
    {#each tags as tag}
      <label>
        <input type="radio" name="tag" value={tag} bind:group={selectedTag} />
        {tag}
      </label>
    {/each}
  </div>
  <div>
    {#each reducers as reducer}
      <label>
        <input type="radio" name="reducer" value={reducer} bind:group={selectedReducer} />
        {reducer}
      </label>
    {/each}
  </div>
  <!-- radio for visible plots -->
  <div>
    {#each models as model, i}
      <label>
        <input type="checkbox" bind:checked={visible_plots[i]} />
        {model}
      </label>
    {/each}
  </div>
  <!-- radio for number of columns -->
  <div>
    {#each [2, 3] as size}
      <label>
        <input type="radio" name="column_size" value={size} bind:group={column_size} />
        {size} columns
      </label>
    {/each}
  </div>
</div>

<div class="plots" style="--grid-size:{column_size}">
  {#each models as model, i}
    {#if visible_plots[i]}
      <div>
        <h2>{model}</h2>
        <img
          src={buildPlotUrl(model, selectedGroup, selectedTag, selectedReducer)}
          alt="plot of {selectedTag} in {model} using {selectedReducer}"
        />
      </div>
    {/if}
  {/each}
</div>

<style>
  /* put a black border around the selection divs, and add a pixel of space */
  .selectors div {
    border: 1px solid black;
    margin: 1px;
  }

  /* put the plots in a 3 column grid if the screen is wide enough, adjusting
  the size of the plots to be half width */
  @media (min-width: 600px) {
    .plots {
      display: grid;
      grid-template-columns: repeat(var(--grid-size, 2), 1fr);
    }
  }
  .plots img {
    width: 100%;
  }
</style>
