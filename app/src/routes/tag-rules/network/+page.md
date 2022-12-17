<script>
    import { onMount } from "svelte";
    export let data;
    let GephiNetwork;
    let gephi_assoc;

    onMount(async () => {
        GephiNetwork = (await import("$lib/GephiNetwork.svelte")).default;
        gephi_assoc = data.gephi_assoc;
    })

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

<svelte:component this={GephiNetwork} data={gephi_assoc} {options} selectedNode={"Isekai"} />

## notes

The layout is generate using [Gephi](https://gephi.org/).
We apply the [Yifan Hu](https://gephi.org/tutorials/gephi-tutorial-layouts.pdf) layout to the network.
The nodes are colored by classes found using [modularity clustering](<https://en.wikipedia.org/wiki/Modularity_(networks)>).
Hover over a node to see it's name and the association rules that it is a part of.

### todo

- Add more layouts to visualize the network.
- Provide a way to grey out nodes that are not connected to the selected node.
