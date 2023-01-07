<script>
  // a bar chart that shows how far the personal library is from various tags
  import { onMount } from "svelte";
  import { library_edits, getLibrary } from "$lib/personalization.js";
  import { browser } from "$app/environment";
  import PolarChart from "$lib/PolarChart.svelte";

  export let data = [];

  export let group = "genre";
  export let min_support_step = 0.0;
  export let layout = {};
  let min_support = 0.0;
  let ignore_tags = [];

  onMount(async () => {
    data = await getLibrary();
    $library_edits += 1;
  });

  $: browser &&
    $library_edits &&
    getLibrary().then((library) => {
      data = library;
      $library_edits = 0;
    });

  $: ref_tags = data.filter((row) => row.tags.length > 0).map((row) => row.tags.map((t) => t.name));
</script>

<!-- add radio options to change the group between genre, theme, and format -->

<div class="container">
  <PolarChart {ref_tags} {group} {min_support_step} {ignore_tags} {layout} bind:min_support />
  <div class="options">
    {#each ["genre", "theme", "format"] as g}
      <input type="radio" name="group" value={g} bind:group />
      <label for={g}>{g}</label>
    {/each}
  </div>
  <div class="options">
    <!-- slider for min_support -->
    <label for="min_support">min support</label>
    <input
      type="range"
      name="min_support"
      min={0.0}
      max={0.99}
      step={0.01}
      bind:value={min_support_step}
    />
    {min_support.toFixed(4)}
  </div>
</div>

<style>
  .container {
    justify-content: center;
  }
  .options {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
  }
</style>
