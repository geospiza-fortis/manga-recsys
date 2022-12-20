<script>
  export let group_id;
  export let element;
  let data;

  async function get_group_info(group_id) {
    let resp = await fetch(`/api/v1/metadata/group_info/${group_id}.json`);
    return await resp.json();
  }

  $: group_id && get_group_info(group_id).then((r) => (data = r[0]));
</script>

<div bind:this={element}>
  {#if data}
    <h2>{data.name} ({!data.inactive ? "active" : "inactive"})</h2>
    <!-- Created at yyyy-mm-dd, updated at yyyy-mm-dd -->
    <i>Created {data.createdAt.substring(0, 10)}, updated {data.updatedAt.substring(0, 10)}</i>
    {#if data.description}
      <p>{data.description}</p>
    {/if}
  {:else}
    <p>Loading...</p>
  {/if}
</div>
