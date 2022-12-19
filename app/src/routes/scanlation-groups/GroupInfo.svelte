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
    <h1>{data.name}</h1>
    <p>{data.description}</p>
  {/if}
  {JSON.stringify(data)}
</div>
