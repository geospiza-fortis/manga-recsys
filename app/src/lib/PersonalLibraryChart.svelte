<script>
  // a bar chart that shows how far the personal library is from various tags
  import { onMount } from "svelte";
  import {
    library_edits,
    getLibrary,
    fetchTagWordVectors,
    fetchSortedTags,
    computeMeanVector,
    computeTagVector,
    computeVectorSimilarity
  } from "$lib/personalization.js";
  import { browser } from "$app/environment";
  import Plot from "$lib/Plot.svelte";

  export let data = [];

  let sorted_tags = [];
  let group = "genre";
  let min_support_step = 0.0;
  let ignore_tags = [];

  let word_vectors = new Map();

  onMount(async () => {
    data = await getLibrary();
    word_vectors = await fetchTagWordVectors();
    sorted_tags = await fetchSortedTags("euclidean");
    $library_edits += 1;
  });

  $: browser &&
    $library_edits &&
    getLibrary().then((library) => {
      data = library;
      $library_edits = 0;
    });

  function computePersonalVector(data, word_vectors) {
    if (data.length == 0) return [];
    if (word_vectors.size == 0) return [];
    let manga_vectors = data.map((row) =>
      computeTagVector(
        row.tags.map((t) => t.name),
        word_vectors
      )
    );
    return computeMeanVector(manga_vectors);
  }

  function computeTagGroupVectors(tags, word_vectors) {
    if (tags.length == 0) return [];
    if (word_vectors.size == 0) return [];
    return tags.map((tag) => computeTagVector(tag, word_vectors));
  }

  function computeSimilarities(personal_vector, tag_vectors) {
    if (personal_vector.length == 0) return [];
    if (tag_vectors.length == 0) return [];
    return tag_vectors.map((tag_vector) => computeVectorSimilarity(personal_vector, tag_vector));
  }

  $: personal_vector = computePersonalVector(data, word_vectors);
  $: group_tags = sorted_tags.filter(
    (tag) => tag.group == group && !ignore_tags.includes(tag.name)
  );
  $: range_support_min = Math.min(...group_tags.map((t) => t.support));
  $: range_support_max = Math.max(...group_tags.map((t) => t.support));
  // map min_support_step between min and max, but on a log scale
  $: min_support = min_support_step * (range_support_max - range_support_min) + range_support_min;
  $: min_support = Math.min(min_support, range_support_max);
  $: tags = group_tags.filter((tag) => tag.support > min_support).map((tag) => [tag.name]);
  $: tag_vectors = computeTagGroupVectors(tags, word_vectors);
  $: similarities = computeSimilarities(personal_vector, tag_vectors);

  function transformPolar(data, norm = false, log = false) {
    // all elements sum to 1
    let x = data;
    if (norm) {
      let sum = x.reduce((a, b) => a + b, 0);
      x = x.map((d) => d / sum);
    }
    if (log) {
      x = x.map((d) => Math.log(d + 1));
    }
    return [
      {
        r: [...x, x[0]],
        theta: [...tags, tags[0]].map((t) => t.join(", ")),
        type: "scatterpolargl",
        fill: "toself"
      }
    ];
  }

  $: layout = {
    title: `Personal Library, similarity to ${group} tags`,
    // make the polar plot go to 1
    polar: {
      radialaxis: {
        range: [-1, 1]
      }
    }
  };
</script>

<!-- add radio options to change the group between genre, theme, and format -->

<div>
  {#if similarities && similarities.length > 0}
    <Plot data={similarities} transform={transformPolar} {layout} />
  {/if}
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
  .options {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
  }
</style>
