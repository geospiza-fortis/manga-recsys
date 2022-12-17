<script>
    import Network from "$lib/Network.svelte";
    export let data;
    $: nodes = data.nodes;
    $: edges = data.edges;
    const options = {
        autoResize: true,
        layout: {
            improvedLayout: false
        },
        physics: {
            enabled: true,
            solver: "forceAtlas2Based"
        },
    }
</script>

# tag-rules network

{#if nodes && edges}
<Network {nodes} {edges} {options} />
{/if}
