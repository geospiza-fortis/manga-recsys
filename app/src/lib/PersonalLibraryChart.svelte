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
  $: personal_vector = computePersonalVector(data, word_vectors);
  $: tag_vectors =
    word_vectors.size > 0 ? tags.map((tag) => computeTagVector(tag, word_vectors)) : [];
  $: similarities =
    personal_vector.length && tag_vectors.length
      ? tag_vectors.map((tag_vector) => computeVectorSimilarity(personal_vector, tag_vector))
      : [];

  function transform(data) {
    return [
      {
        x: tags.map((t) => t.join(", ")),
        y: data,
        type: "bar"
      }
    ];
  }
  $: layout = {
    title: "Personal Library",
    xaxis: {
      title: "Tag"
    },
    yaxis: {
      title: "Similarity"
    }
  };
</script>

<Plot data={similarities} {transform} {layout} />
