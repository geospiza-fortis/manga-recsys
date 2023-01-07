<script>
  // a bar chart that shows how far the personal library is from various tags
  import { onMount } from "svelte";
  import {
    fetchTagWordVectors,
    fetchSortedTags,
    computeMeanVector,
    computeTagVector,
    computeVectorSimilarity
  } from "$lib/personalization.js";
  import Plot from "$lib/Plot.svelte";

  // array of array of tags
  export let ref_tags = [];
  export let group = "genre";
  export let min_support_step = 0.0;
  export let ignore_tags = [];
  export let layout = {};

  export let min_support = 0.0;

  let word_vectors = new Map();
  let sorted_tags = [];

  onMount(async () => {
    word_vectors = await fetchTagWordVectors();
    sorted_tags = await fetchSortedTags("euclidean");
  });

  function computeReferenceVector(data, word_vectors) {
    if (data.length == 0) return [];
    if (word_vectors.size == 0) return [];
    let manga_vectors = data.map((tags) => computeTagVector(tags, word_vectors));
    return computeMeanVector(manga_vectors);
  }

  function computeTagGroupVectors(tags, word_vectors) {
    if (tags.length == 0) return [];
    if (word_vectors.size == 0) return [];
    return tags.map((tag) => computeTagVector(tag, word_vectors));
  }

  function computeSimilarities(ref_vector, tag_vectors) {
    if (ref_vector.length == 0) return [];
    if (tag_vectors.length == 0) return [];
    return tag_vectors.map((tag_vector) => computeVectorSimilarity(ref_vector, tag_vector));
  }

  $: ref_vector = computeReferenceVector(ref_tags, word_vectors);
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
  $: similarities = computeSimilarities(ref_vector, tag_vectors);

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

  $: polar_layout = {
    title: `Similarity to ${group} tags`,
    // make the polar plot go to 1
    polar: {
      radialaxis: {
        range: [-1, 1]
      }
    },
    ...layout
  };
</script>

{#if similarities && similarities.length > 0}
  <Plot data={similarities} transform={transformPolar} layout={polar_layout} />
{/if}
