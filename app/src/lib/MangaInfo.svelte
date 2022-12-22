<script>
  export let manga_id;
  export let element;
  let data;

  async function get_manga_info(manga_id) {
    let resp = await fetch(`/api/v1/metadata/manga_info/${manga_id}.json`);
    return await resp.json();
  }

  $: manga_id && get_manga_info(manga_id).then((r) => (data = r[0]));
  const basicInfo = [
    { label: "Original language", key: "originalLanguage" },
    { label: "Demographic", key: "demographic" },
    { label: "Content rating", key: "contentRating" }
  ];
</script>

<div bind:this={element}>
  {#if data}
    <h2>{data.name || data.id}</h2>
    <!-- Created at yyyy-mm-dd, updated at yyyy-mm-dd -->
    <i>Created {data.createdAt.substring(0, 10)}, updated {data.updatedAt.substring(0, 10)}</i>
    <p>
      {#each basicInfo as { label, key }}
        {#if data[key]}
          <span><b>{label}</b>: {data[key]} </span>
        {/if}
      {/each}
    </p>
    <p><b>Tags</b>: {data.tags.map((tag) => tag.name).join(", ")}</p>
    <p />
    <p>{data.description}</p>
  {:else}
    <p>Loading...</p>
  {/if}
</div>
