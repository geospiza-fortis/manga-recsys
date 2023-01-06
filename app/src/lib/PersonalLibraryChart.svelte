<script>
  // a bar chart that shows how far the personal library is from various tags
  import { onMount } from "svelte";
  import {
    library_edits,
    getLibrary,
    fetchTagWordVectors,
    computeMeanVector,
    computeTagVector,
    computeVectorSimilarity
  } from "$lib/personalization.js";
  import { browser } from "$app/environment";
  import Plot from "$lib/Plot.svelte";

  export let data = [];
  let tags = [["Romance"], ["Drama"], ["Adventure"], ["Fantasy"], ["Sports"]];
  let word_vectors = new Map();
  onMount(async () => {
    data = await getLibrary();
    word_vectors = await fetchTagWordVectors();
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

  function computeSimilarities(personal_vector, tag_vectors) {
    if (personal_vector.length == 0) return [];
    if (tag_vectors.length == 0) return [];
    return tag_vectors.map((tag_vector) => computeVectorSimilarity(personal_vector, tag_vector));
  }
  $: personal_vector = computePersonalVector(data, word_vectors);
  $: tag_vectors =
    word_vectors.size > 0 ? tags.map((tag) => computeTagVector(tag, word_vectors)) : [];
  $: similarities = computeSimilarities(personal_vector, tag_vectors);

  function transformPolar(data) {
    // all elements sum to 1
    let sum = data.reduce((a, b) => a + b, 0);
    let normed = data.map((d) => d / sum);
    return [
      {
        r: [...normed, normed[0]],
        theta: [...tags, tags[0]].map((t) => t.join(", ")),
        type: "scatterpolargl",
        fill: "toself"
      }
    ];
  }
  $: layout = {
    title: "Personal Library, Similarity to Tags"
  };
</script>

{#if similarities && similarities.length > 0}
  <Plot data={similarities} transform={transformPolar} {layout} />
{/if}
