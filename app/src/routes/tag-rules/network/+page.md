<script>
    import GephiNetwork from "$lib/GephiNetwork.svelte";
    export let data;
    $: gephi_assoc = data.gephi_assoc;
    const options = {
        autoResize: true,
        layout: {
            improvedLayout: false
        },
        physics: {
            enabled: false,
        },
        interaction: {
            hover: true,
            dragNodes: false,
            tooltipDelay: 150
        }
    }
</script>

# tag-rules network

A network visualization of the [tag rules](/tag-rules) data.

{#if gephi_assoc }
<GephiNetwork data={gephi_assoc} {options} />
{/if}

## notes

The layout is generate using [Gephi](https://gephi.org/).
We apply the [Yifan Hu](https://gephi.org/tutorials/gephi-tutorial-layouts.pdf) layout to the network.
The nodes are colored by classes found using [modularity clustering](<https://en.wikipedia.org/wiki/Modularity_(networks)>).
Hover over a node to see it's name.

### todo

- Add more layouts to visualize the network.
- Provide a way to grey out nodes that are not connected to the hovered node.
- Add a table showing all of the related nodes.