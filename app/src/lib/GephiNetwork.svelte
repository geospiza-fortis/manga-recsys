<script>
  import { networkGephiParser } from "vis-network/standalone";
  import Network from "./Network.svelte";
  import { browser } from "$app/environment";

  export let data = null;
  export let options = {};
  export let network = null;

  export let selectedNode = null;
  let toNodes = [];
  let fromNodes = [];

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
  $: network && network.on("selectNode", (params) => (selectedNode = params.nodes[0]));
  $: network && selectedNode && (toNodes = network.getConnectedNodes(selectedNode, "to"));
  $: network && selectedNode && (fromNodes = network.getConnectedNodes(selectedNode, "from"));
</script>

{#if parsed}
  <Network
    nodes={parsed.nodes.map((obj) => ({ title: obj.id, ...obj }))}
    edges={parsed.edges}
    {options}
    bind:network
  />
  <!-- make this part of a 3 column flexbox -->
  <div class="info">
    {#if fromNodes.length > 0}
      <div>
        <h3>Antecdents</h3>
        <ul>
          {#each fromNodes as node}
            <li>
              <button class="clickable" on:click={() => (selectedNode = node)}>{node}</button>
            </li>
          {/each}
        </ul>
      </div>
    {/if}
    {#if selectedNode}
      <div>
        <h3>Selected node</h3>
        <p>{selectedNode}</p>
      </div>
    {/if}
    {#if toNodes.length > 0}
      <div>
        <h3>Consequents</h3>
        <ul>
          {#each toNodes as node}
            <li>
              <button class="clickable" on:click={() => (selectedNode = node)}>{node}</button>
            </li>
          {/each}
        </ul>
      </div>
    {/if}
  </div>
{/if}

<style>
  .info {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    margin-top: 1rem;
  }
  .clickable {
    cursor: pointer;
  }
</style>
