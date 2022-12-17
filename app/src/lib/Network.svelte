<script>
  import { DataSet, Network } from "vis-network/standalone";
  import { browser } from "$app/environment";

  // nodes are a list of id, label pairs
  // edges are a list of from, to pairs

  export let nodes = [];
  export let edges = [];
  export let options = {};
  export let network = null;
  let params = null;

  let element;
  $: element &&
    browser &&
    (network = new Network(
      element,
      {
        nodes: new DataSet(nodes),
        edges: new DataSet(edges)
      },
      options
    ));
  $: network &&
    network.on("stabilizationProgress", (p) => (params = { ...p })) &&
    network.on("stabilizationIterationsDone", () => {
      params = null;
      // turn off physics
      network.setOptions({ physics: { enabled: false } });
    });
</script>

{#if params && params.iterations > 0}
  <p>Stabilizing network... {params.iterations}/{params.total} iterations remaining</p>
{/if}
<div class="network" bind:this={element} />

<style>
  .network {
    width: 100%;
    height: 600px;
    border: 1px solid lightgray;
  }
</style>
