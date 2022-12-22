<script>
  let container;
  function onLoad() {
    Redoc.init("/openapi/openapi.yaml", { scrollYOffset: 50 }, container);
  }
</script>

<svelte:head>
  <!-- refresh the script if we've loaded the page again -->
  {#if container}
    <script
      src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"
      on:load={onLoad}
    ></script>
  {/if}
</svelte:head>

<div class="redoc" bind:this={container} />
