<script>
  import { merge } from "lodash-es";
  export let data;
  export let transform = (res) => res;
  export let layout = {};
  let plotElement;

  function onLoad() {
    // console.log(transform(data));
    try {
      Plotly.newPlot(
        plotElement,
        transform(data),
        merge(
          {
            margin: {
              l: 50,
              r: 0,
              b: 50
            }
          },
          layout
        ),
        { responsive: true }
      );
    } catch (e) {
      console.log(e);
    }
  }
  $: plotElement && data && data.length && onLoad();
</script>

<svelte:head>
  {#if plotElement && data && data.length}
    <script src="https://cdn.plot.ly/plotly-2.16.1.min.js" on:load={onLoad}></script>
  {/if}
</svelte:head>

<div bind:this={plotElement} />
