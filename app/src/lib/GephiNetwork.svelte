<script>
  import { networkGephiParser } from "vis-network/esnext";
  import Network from "./Network.svelte";
  import { browser } from "$app/environment";

  export let data = null;
  export let options = {};
  export let network = null;
  let parsed;
  $: browser &&
    (parsed = networkGephiParser.parseGephi(data, {
      edges: {
        inheritColor: false
      },
      nodes: {
        fixed: true,
        parseColor: false
      }
    }));
</script>

{#if parsed}
  <Network
    nodes={parsed.nodes.map((obj) => ({ title: obj.id, ...obj }))}
    edges={parsed.edges}
    {options}
    bind:network
  />
{/if}
